import sys
import os.path
from io import StringIO
from abc import ABCMeta
from ast import Node, DeleteNode


#
# Traversals
#


class ASTVisitor(object):
    '''
    Base class for traversing the AST. It allows you to specify custom behaviour
    for any AST node by defining a `visit<node-name>` method, e.g., `def
    visitProgram(self, program): ...`. By default, the visitor recursively
    visits all child nodes of a node.

    Use `self.visit_children` in a custom visitor method to traverse the child
    nodes of a node without explicitly having to specify the attribute names.
    '''
    __metaclass__ = ABCMeta

    def visit(self, node):
        if isinstance(node, list):
            for child in node:
                self.visit(child)
        elif isinstance(node, Node):
            if not self.visit_try_class(node, node.__class__):
                self.visit_children(node)

    def visit_try_class(self, node, cls):
        func = getattr(self.__class__, 'visit' + cls.__name__, None)

        if callable(func):
            func(self, node)
            return True

        if cls is Node:
            return False

        for base in cls.__bases__:
            if self.visit_try_class(node, base):
                return True

    def visit_children(self, node):
        for name, child in node.iter_children():
            self.visit(child)


class ASTTransformer(object):
    '''
    Base class for transforming traversals. Similar to `ASTVisitor` but also
    assigns any returned value to the appropriate attribute of the parent node.
    See `desugar.Desugarer` for an illustrative example.
    '''
    __metaclass__ = ABCMeta

    def visit(self, node):
        if isinstance(node, list):
            replacement = []

            for child in node:
                result = self.visit(child)

                if isinstance(result, list):
                    replacement += result
                elif not isinstance(result, DeleteNode):
                    replacement.append(child if result is None else result)

            return replacement

        if not isinstance(node, Node):
            return

        found, result = self.visit_try_class(node, node.__class__)
        if found:
            return result

        self.visit_children(node)

    def visit_try_class(self, node, cls):
        func = getattr(self.__class__, 'visit' + cls.__name__, None)

        if callable(func):
            return True, func(self, node)

        if cls is not Node:
            for base in cls.__bases__:
                found, result = self.visit_try_class(node, base)
                if found:
                    return True, result

        return False, None

    def visit_children(self, node):
        for name, child in node.iter_children():
            result = self.visit(child)
            if result is not None:
                if isinstance(result, DeleteNode):
                    result = None
                setattr(node, name, result)


class PrintTree(ASTVisitor):
    '''
    Example of custom `ASTVisitor`, prints the structure of an AST.
    '''
    def __init__(self):
        self.indents = 0

    def visitNode(self, node):
        print(self.indents * '  ' + node.__class__.__name__)
        self.indents += 1
        self.visit_children(node)
        self.indents -= 1


#
# Error handling
#


class LocationError(Exception):
    '''
    Error raised at a location tuple. Displays the error message and higlights
    the accompanying source code line.
    '''

    def __init__(self, location, message, *args):
        self.location = location
        self.message = message % args

    def print(self, showsrc, code=None, fout=sys.stderr):
        fname, ystart, xstart, yend, xend = self.location

        if yend != ystart:
            sline = 'lines %d-%d' % (ystart, yend)
        else:
            sline = 'line %d' % ystart

        if xend != xstart:
            scol = 'characters %d-%d' % (xstart, xend)
        else:
            scol = 'character %d' % xstart

        print("File \"%s\", %s, %s:\n%s" % (fname, sline, scol, self.message),
                file=fout)

        if not showsrc:
            return

        tab = '    '

        if os.path.isfile(fname):
            f = open(fname)
        elif code is not None:
            f = StringIO(code)
        else:
            raise Exception('Error: could not find source file to print error: %s' % fname)

        for i, line in enumerate(f):
            l = i + 1
            line = line.rstrip()

            # retab tabs to spaces
            ntabs = 0
            for c in line:
                if c != '\t':
                    break
                ntabs += 1
            line = tab * ntabs + line[ntabs:]

            if l >= ystart:
                if line:
                    left = xstart - 1 if l == ystart else ntabs * len(tab)
                    right = xend if l == yend else len(line)
                    width = right - left
                    print(line, file=fout)
                    print((left + ntabs * (len(tab) - 1)) * ' ' + width * '^', file=fout)

                if l == yend:
                    break

        f.close()


class NodeError(LocationError):
    '''
    Error raised at an AST node. Displays the error message and higlights the
    accompanying source code line. Use like this:
    >>> raise NodeError(node, 'error message')
    '''
    def __init__(self, node, message, *args):
        super(NodeError, self).__init__(node.location, message, *args)
        self.node = node

    def print(self, showsrc, code=None, fout=sys.stderr):
        hasloc = self.node.location[0] is not None
        super(NodeError, self).print(showsrc and hasloc, code, fout)

        if showsrc and not hasloc:
            print('node:', repr(self.node))


class BackrefError(LocationError):
    '''
    Error raised at two source location tuples. Displays two error messages at
    two separate;ly highlighted source lines. Used to also show a definition
    while raising an error at a use.
    '''
    def __init__(self, loc, msg, refloc, refmsg):
        super(BackrefError, self).__init__(loc, msg)
        self.refloc = refloc
        self.refmsg = refmsg

    def print(self, showsrc, code=None, fout=sys.stderr):
        LocationError.print(self, showsrc, code, fout)
        LocationError(self.refloc, self.refmsg).print(showsrc, code, fout)


class FatalError(BaseException):
    '''
    Used for miscellanious errors for which e don't want to print a backtrace.
    '''
    pass
