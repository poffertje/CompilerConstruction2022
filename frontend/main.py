#!/usr/bin/env python3
import sys
import os.path
import argparse
import re
import pkg_resources

pkg_resources.require('ply')
pkg_resources.require('llvmlite==0.34.*')

import llvmlite.binding as llvm

from util import LocationError, FatalError
from parser import preprocess, parse
from desugar import Desugarer
from context import ContextAnalysis
from typecheck import TypeChecker
from irgen import IRGen


all_phases =[
    'preprocess', 'parser', 'desugar', 'context', 'typecheck', 'irgen'
]


def dump(args, prog, phase, print_if_verbose, width=80):
    if args.verbose:
        lfill = rfill = '-' * int((width - len(phase) - 2) / 2)
        if len(phase) % 2:
            rfill += '-'
        print(lfill, phase, rfill, file=sys.stderr)

        if print_if_verbose:
            print(prog, file=sys.stderr)

    if args.dump_after == phase:
        print(prog)
        sys.exit(0)


def save_module(args, module):
    mod = llvm.parse_assembly(str(module))
    mod.verify()

    if args.emit_bc:
        with os.fdopen(args.outfile.fileno(), 'wb') as f:
            f.write(mod.as_bitcode())
    else:
        args.outfile.write(str(mod))


def add_default_include_paths(args):
    # add working dir and parent dir of source file to include path
    args.include_paths.append('.')

    if args.infile is not sys.stdin:
        dirname = os.path.dirname(args.infile.name)
        fulldir = os.path.abspath(dirname)
        args.include_paths.append(fulldir)


def infile_base(args):
    print('base:', re.sub(r'\.f?[cC]$|^<|>$', '', args.infile.name))
    return re.sub(r'\.f?[cC]$|^<|>$', '', args.infile.name)


def fix_file_args(args):
    if args.verbose:
        args.outfile = sys.stdout
        args.emit_ll = True

    elif args.outfile is None:
        if args.infile is sys.stdin:
            args.outfile = sys.stdout
            args.emit_ll = True
        else:
            extension = '.bc' if args.emit_bc else '.ll'
            args.outfile = open(infile_base(args) + extension, 'w')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-cpp', dest='preprocess', action='store_false',
            help='do not run the preprocessor')
    parser.add_argument('infile', nargs='?',
            type=argparse.FileType('r'), default=sys.stdin,
            help='input file to compile (default stdin)')
    parser.add_argument('-v', '--verbose', action='store_true',
            help='enable all intermediate dumps and write IR to stdout')
    parser.add_argument('-o', '--outfile', metavar='FILE',
            type=argparse.FileType('w'), default=None,
            help='output file (defaults to infile with .ll extension)')
    parser.add_argument('--emit-bc', action='store_true',
            help='write output as bitcode (produces .bc instead of .ll)')
    parser.add_argument('-d', '--dump-after', choices=all_phases,
            help='dump AST/IR to stdout and exit after specified phase')
    parser.add_argument('-I', metavar='PATH', dest='include_paths',
            action='append', default=[],
            help='add include path for preprocessor')
    args = parser.parse_args()

    try:
        add_default_include_paths(args)
        fix_file_args(args)
        origsrc = src = args.infile.read()

        if args.preprocess:
            src = preprocess(args.infile.name, src, args.include_paths)
            dump(args, src, 'preprocess', True)

        tree = parse(args.infile.name, src)
        dump(args, tree, 'parser', True)
        tree.verify()

        Desugarer().visit(tree)
        dump(args, tree, 'desugar', True)
        tree.verify()

        ContextAnalysis().visit(tree)
        dump(args, tree, 'context', False)
        tree.verify()

        TypeChecker().visit(tree)
        dump(args, tree, 'typecheck', False)
        tree.verify()

        module = IRGen(args.infile.name).visit(tree)
        dump(args, module, 'irgen', False)
        save_module(args, module)

    except EOFError:
        print('Syntax error: unexpected end of file', file=sys.stderr)
        sys.exit(1)
    except LocationError as e:
        e.print(True, origsrc)
        sys.exit(1)
    except (IOError, FatalError) as e:
        print('Error: %s' % e, file=sys.stderr)
        sys.exit(1)
