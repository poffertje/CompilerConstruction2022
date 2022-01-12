#!/usr/bin/env python3
import sys
import os
import glob
import traceback
import subprocess
import pkg_resources
from io import StringIO
import llvmlite.binding as llvm
from termcolor import colored

from util import LocationError, FatalError
from parser import preprocess, create_parser, parse
from desugar import Desugarer
from context import ContextAnalysis
from typecheck import TypeChecker
from irgen import IRGen
from ast import ASTError
from main import all_phases

pkg_resources.require('ply')
pkg_resources.require('llvmlite==0.34.*')
pkg_resources.require('termcolor')

tests_dir = 'test'
fennec_ext = '.fc'
alignment = 60

root_path = os.path.dirname(os.path.abspath(__file__))
tests_path = root_path + '/' + tests_dir
parser = create_parser(debug=True)


class TestCase:
    default_timeout = 3.0 # in seconds, overwriteable with envvar TIMEOUT

    def __init__(self, path, phase, test_type, basename):
        self.path = path
        self.phase = phase
        self.test_type = test_type
        self.basename = basename
        self.ferr = StringIO()
        self.generated_files = []

    def run(self):
        showpath = self.path + ':'
        sys.stdout.write('%%-%ds' % alignment % showpath)

        if self.test_autodetect():
            print(colored('ok', 'green', attrs=['bold']))
            self.cleanup()
            return True
        else:
            print(colored('failed', 'red', attrs=['bold']))
            sys.stdout.write(self.ferr.getvalue())
            return False

    def test_autodetect(self):
        if self.test_type == 'success':
            return self.test_success()

        if self.test_type == 'error':
            return self.test_error()

        if self.test_type == 'dump':
            return self.test_dump()
        if self.test_type == 'run':
            try:
                return self.test_run()
            except subprocess.TimeoutExpired:
                return False
        if self.test_type == 'run-group':
            try:
                return self.test_run_group()
            except subprocess.TimeoutExpired:
                return False

        raise FatalError('invalid test type: ' + self.test_type)

    def test_success(self):
        return self.compile_fennec(self.path, self.phase) is not None

    def test_error(self):
        return self.compile_fennec(self.path, self.phase) is None

    def test_dump(self):
        tree = self.compile_fennec(self.path, self.phase)
        if tree is None:
            return False

        got = str(tree)
        expectfile = self.path.replace(fennec_ext, '-expect' + fennec_ext)
        return self.assert_equal(got + '\n', expectfile)

    def test_run(self):
        if phase != 'irgen':
            raise FatalError('run test in phase %s makes no sense' % phase)

        module = self.compile_fennec(self.path)
        if module is None:
            return False

        if not self.compile_llvm(module, self.path):
            return False

        exefile = self.path.replace(fennec_ext, '')
        if not self.link(exefile, [self.path]):
            return False

        output = self.run_binary(exefile)
        expectfile = self.path.replace(fennec_ext, '.out')
        return self.assert_equal(output, expectfile)

    def test_run_group(self):
        if phase != 'irgen':
            raise FatalError('run test in phase %s makes no sense' % phase)

        fcfiles = glob.glob(self.path + '/*.fc')
        if not len(fcfiles):
            raise FatalError('no .fc files found in ' + self.path)

        for fcpath in fcfiles:
            module = self.compile_fennec(fcpath)
            if module is None or not self.compile_llvm(module, fcpath):
                return False

        exefile = self.path + '/' + os.path.basename(self.path)
        if not self.link(exefile, fcfiles):
            return False

        output = self.run_binary(exefile)
        expectfile = self.path + '/expected.out'
        return self.assert_equal(output, expectfile)

    def assert_equal(self, got, expectfile):
        res = subprocess.run(['diff', '--side-by-side', '-', expectfile],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             input=got.encode('ascii'))
        self.ferr.write(res.stdout.decode('ascii'))
        return res.returncode == 0

    def compile_fennec(self, fcpath, stop_after=None):
        try:
            with open(fcpath) as f:
                origsrc = f.read()

            include_paths = [tests_path, os.path.dirname(fcpath)]
            src = preprocess(fcpath, None, include_paths)
            if stop_after == 'preprocess':
                return src

            tree = parse(fcpath, src, parser=parser)
            tree.verify()
            if stop_after == 'parser':
                return tree

            Desugarer().visit(tree)
            tree.verify()
            if stop_after == 'desugar':
                return tree

            ContextAnalysis().visit(tree)
            tree.verify()
            if stop_after == 'context':
                return tree

            TypeChecker().visit(tree)
            tree.verify()
            if stop_after == 'typecheck':
                return tree

            basename = os.path.basename(fcpath).replace(fennec_ext, '')
            module = IRGen(basename).visit(tree)
            if stop_after == 'irgen':
                return module

            llmodule = llvm.parse_assembly(str(module))
            llmodule.verify()

            llfile = fcpath.replace(fennec_ext, '.ll')
            with open(llfile, 'w') as f:
                f.write(str(llmodule))
            self.generated_files.append(llfile)

            return llmodule

        except EOFError:
            print('Syntax error: unexpected end of file', file=self.ferr)
        except LocationError as e:
            e.print(True, origsrc, fout=self.ferr)
        except (IOError, FatalError) as e:
            print('Error: %s' % e, file=self.ferr)
        except (NotImplementedError, ASTError):
            traceback.print_exc(file=self.ferr)
        except:
            print('Error: frontend crashed', file=self.ferr)
            traceback.print_exc(file=self.ferr)

    def compile_llvm(self, module, fcpath):
        ofile = fcpath.replace(fennec_ext, '.o')
        res = subprocess.run(['llc', '-filetype=obj', '-o', ofile, '-'],
                             input=module.as_bitcode(), stderr=subprocess.PIPE)
        self.generated_files.append(ofile)
        self.ferr.write(res.stderr.decode('ascii'))
        return res.returncode == 0

    def link(self, outfile, fcfiles):
        ofiles = [f.replace(fennec_ext, '.o') for f in fcfiles]
        res = subprocess.run(['clang', '-o', outfile] + ofiles,
                             stderr=subprocess.PIPE)
        self.generated_files.append(outfile)
        self.ferr.write(res.stderr.decode('ascii'))
        return res.returncode == 0

    def run_binary(self, path):
        timeout = float(os.getenv('TIMEOUT', default=self.default_timeout))
        res = subprocess.run([path], stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, timeout=timeout)
        outfile = path + '.run'
        with open(outfile, 'wb') as f:
            f.write(res.stdout)
        self.generated_files.append(outfile)
        return res.stdout.decode('ascii')

    def cleanup(self):
        while len(self.generated_files):
            path = self.generated_files.pop()
            if os.path.exists(path):
                os.remove(path)


def phase_files(phase):
    for f in glob.glob('%s/%s/*/*.fc' % (tests_path, phase)):
        if not f.endswith('-expect' + fennec_ext):
            yield f

    for d in glob.glob('%s/%s/run-group/*' % (tests_path, phase)):
        if not os.path.isdir(d):
            raise FatalError('invalid test: ' + d)
        yield d


def expand_dirs(*paths):
    for path in paths:
        # normalize to root dir
        path = os.path.abspath(path)
        if not path.startswith(tests_path):
            raise FatalError('test files must be in %s' % tests_path)
        path = path[len(root_path) + 1:]

        # expand directory contents
        if os.path.isdir(path):
            if 'run-group/' in path:
                yield path
            else:
                for child in sorted(glob.glob(path + '/*')):
                    if os.path.isdir(child):
                        yield from expand_dirs(child)
                    elif child.endswith(fennec_ext):
                        if not child.endswith('-expect' + fennec_ext):
                            yield child
        elif path.endswith(fennec_ext):
            yield path
        else:
            raise FatalError('invalid test: ' + path)


def parse_test_path(path):
    parts = path.split('/')

    if os.path.isdir(path):
        if parts[-2] != 'run-group':
            raise FatalError('invalid test: ' + path)
    elif not path.endswith(fennec_ext):
        raise FatalError('invalid test: ' + path)

    return (path,) + tuple(parts[-3:])


if __name__ == '__main__':
    try:
        # collect tests to run
        if len(sys.argv) == 1:
            files = [tests_path + '/' + phase for phase in all_phases
                     if os.path.isdir(tests_path + '/' + phase)]
        else:
            files = sys.argv[1:]
        files = list(expand_dirs(*files))

        # change into frontend root directory to be able to strip its location
        # from absolute paths
        os.chdir(root_path)

        # run tests, count total and failed
        total = failed = 0

        for path in files:
            path, phase, test_type, basename = parse_test_path(path)
            if not TestCase(path, phase, test_type, basename).run():
                failed += 1
            total += 1

        print('%d tests, %d failures' % (total, failed))

    except FatalError as e:
        print('Error: %s' % e, file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print('\nCancelled tests because of keyboard interrupt')
        sys.exit(1)
