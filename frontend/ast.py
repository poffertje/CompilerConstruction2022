import builtins
from abc import ABCMeta


class Type(object):
    '''
    Base class for types in the AST. Do *NOT* instantiate it directly, but
    rather use the static `get` method with the type as a string argument. You
    can also pass array types like 'int[]' to `get` which will return an
    `ArrayType`.
    '''
    base_types = frozenset(['bool', 'char', 'int', 'void'])
    int_bits = 32
    cache = {}

    def __init__(self, name):
        assert name in self.base_types
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    @classmethod
    def get(cls, name):
        if name.endswith('[]'):
            return cls.cache.setdefault(name, ArrayType(cls.get(name[:-2])))

        return cls.cache.setdefault(name, cls(name))

    def is_array(self):
        return False


class ArrayType(Type):
    def __init__(self, base):
        self.base = base

    def __str__(self):
        return str(self.base) + '[]'

    @classmethod
    def get(cls, base):
        return Type.get(str(base) + '[]')

    def is_array(self):
        return True


class Operator(object):
    '''
    Class for operators in the AST. Do *NOT* instantiate it directly, but rather
    use the static `get` method with the operator as a string argument.
    '''
    ops_arithmetic = '+ - * / %'.split()
    ops_equality = '== !='.split()
    ops_relational = '< > <= >='.split()
    ops_logical = '&& || !'.split()
    ops_all = frozenset(ops_arithmetic + ops_equality + ops_relational +
            ops_logical)

    cache = {}

    def __init__(self, op):
        assert op in self.ops_all
        self.op = op

    def __str__(self):
        return self.op

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.op == other

    def __ne__(self, other):
        return self.op != other

    @classmethod
    def get(cls, sign):
        return cls.cache.setdefault(sign, cls(sign))

    def is_arithmetic(self):
        return self.op in self.ops_arithmetic

    def is_equality(self):
        return self.op in self.ops_equality

    def is_relational(self):
        return self.op in self.ops_relational

    def is_logical(self):
        return self.op in self.ops_logical


class ASTError(BaseException):
    '''
    Raised by `Node.verify` finds an error in the AST.
    '''
    pass


class Node(object):
    '''
    Base class for all AST nodes. It contains a bunch of magic you should not
    care about or read. Just read the README and look at the node definitions
    below (from `Program` onwards) to see how it is used.
    '''
    __metaclass__ = ABCMeta  # this makes the class abstract (uninstantiatable)

    children = []
    types = {}

    def __init__(self, *args, **kwargs):
        for i, name in enumerate(self.__class__.children):
            if i < len(args):
                value = args[i]
            elif name in kwargs:
                value = kwargs[name]
            elif self.__class__.types[name].endswith('?'):
                value = None
            else:
                raise RuntimeError('missing initalizer %s for %s' %
                        (name, self.__class__.__name__))

            setattr(self, name, value)

        self.location = (None, 0, 0, 0 ,0)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        s = '<%s' % self.__class__.__name__

        for name, child in self.iter_children():
            childrep = '<Block>' if isinstance(child, Block) else repr(child)
            s += ' %s=%s' % (name, childrep)

        return s + '>'

    def iter_children(self):
        for name in self.__class__.children:
            child = getattr(self, name)
            yield name, child

    def verify(self):
        myname = self.__class__.__name__

        for name in self.__class__.children:
            child = getattr(self, name)
            ty = self.types[name]

            if ty.endswith('?'):
                ty = ty[:-1]
            elif child is None:
                raise ASTError('non-optional child %s.%s has value None: %s' %
                        (myname, name, repr(self)))

            if ty.endswith('*'):
                if not isinstance(child, list):
                    print(repr(self))
                    raise ASTError('%s.%s should have type %s: %s' %
                            (myname, name, ty, child))
                ty = ty[:-1]

            if ty.endswith('+'):
                if not isinstance(child, list):
                    raise ASTError('%s.%s should have type %s: %s' %
                            (myname, name, ty, child))
                if len(child) == 0:
                    raise ASTError('%s.%s should not be empty: %s' %
                            (myname, name, repr(self)))
                ty = ty[:-1]

            cls = globals()[ty] if ty in globals() else getattr(builtins, ty)

            if isinstance(child, list):
                for i, node in enumerate(child):
                    if not isinstance(node, cls):
                        raise ASTError('%s.%s[%d] should have type %s (found %s): %s' %
                                (myname, name, i, ty, type(node).__name__, repr(self)))
            elif not isinstance(child, cls) and child is not None:
                raise ASTError('%s.%s should have type %s (found %s): %s' %
                        (myname, name, ty, type(child).__name__, repr(self)))

            if isinstance(child, Node):
                child.verify()
            elif isinstance(child, list):
                for node in child:
                    if isinstance(node, Node):
                        node.verify()

    def at(self, location):
        '''
        Call this with either a location tuple:
        (filename, ystart, xstart, yend, xend)
        or with another `Node` object to copy the location attribute onto this
        node. Returns the current node to allow method chaining.
        '''
        if isinstance(location, Node):
            self.location = location.location
            if hasattr(location, 'ty'):
                self.ty = location.ty
        else:
            self.location = tuple(location)
        return self


#
# Below are all node definitions for the Abstract Syntax Tree (AST).
#
# AST node definitions have `children` and `types` attributes which serve two
# purposes: first, they tell the parent class `Node` to which attributes
# constructor arguments must be assigned. For instance, `Program` only has a
# `decls` child, which means you can construct a program node by calling
# `Program([decl1, decl2, ...])`.
#
# Second, the type of the attribute is 'Declaration+'. This is used during AST
# verification. Verification is done after each phase to check if a bug in the
# compiler produced an incorrect AST. 'Declaration+' means "a non-empty list of
# `Declaration` objects". Similarly, 'Obj*' means "a list of zero or more
# `Obj`s" and 'Obj?' means "an `Obj` instance or `None`".
#
# Each node definition requires a `__str__` definition as well, which is used
# for pretty-printing the AST as (legal) source code.
#


class Program(Node):
    children = ['decls']
    types = dict(decls='Declaration+')

    def __str__(self):
        return '\n\n'.join(map(str, self.decls))


class Declaration(Node):
    __metaclass__ = ABCMeta


class GlobalDec(Declaration):
    children = ['_type', 'name']
    types = dict(_type='Type', name='str')

    def __str__(self):
        return 'extern {0._type} {0.name};'.format(self)


class GlobalDef(Declaration):
    children = ['static', '_type', 'name', 'value']
    types = dict(static='bool', _type='Type', name='str', value='Expression')

    def __str__(self):
        return '{static}{0._type} {0.name} = {0.value};'.format(self,
                static='static ' if self.static else '')


class FunDec(Declaration):
    children = ['name', '_type']
    types = dict(name='str', _type='FunType')

    def __str__(self):
        return 'extern %s;' % self._type.tostring(self.name)


class FunDef(Declaration):
    children = ['static', 'name', '_type', 'body']
    types = dict(static='bool', name='str', _type='FunType', body='Block')

    def __str__(self):
        return '{static}{ty} {0.body}'.format(self,
                static='static ' if self.static else '',
                ty=self._type.tostring(self.name))


class FunType(Node):
    children = ['return_type', 'params', 'varargs']
    types = dict(return_type='Type', params='Param*', varargs='bool')

    def tostring(self, name):
        dots = ''
        if self.varargs:
            dots = ', ...' if len(self.params) else '...'
        return '{0.return_type} {name}({params}{dots})'.format(self,
                name=name,
                params=', '.join(map(str, self.params)),
                dots=dots)


class Param(Node):
    children = ['_type', 'name']
    types = dict(_type='Type', name='str')

    def __str__(self):
        return '{0._type} {0.name}'.format(self)


class Statement(Node):
    __metaclass__ = ABCMeta


class Assignment(Statement):
    children = ['ref', 'value']
    types = dict(ref='Reference', value='Expression')

    def __str__(self):
        return '{0.ref} = {0.value};'.format(self)


class Modification(Statement):
    children = ['ref', 'op', 'value']
    types = dict(ref='Reference', op='Operator', value='Expression')

    def __str__(self):
        return '{0.ref} {0.op}= {0.value};'.format(self)


class If(Statement):
    children = ['cond', 'yesbody', 'nobody']
    types = dict(cond='Expression', yesbody='Block', nobody='Block?')

    def __str__(self):
        s = 'if ({0.cond}) {0.yesbody}'.format(self)
        if self.nobody:
            s += ' else ' + str(self.nobody)
        return s


class Return(Statement):
    children = ['value']
    types = dict(value='Expression?')

    def __str__(self):
        return 'return;' if self.value is None else 'return {0.value};'.format(self)


class Block(Statement):
    children = ['statements']
    types = dict(statements='Statement*')

    def __str__(self):
        if not self.statements:
            return '{}'

        code = '\n'.join(map(str, self.statements))
        tab = '    '
        indented = tab + code.replace('\n', '\n' + tab).rstrip()
        return '{\n%s\n}' % indented


class VarDef(Statement):
    children = ['_type', 'name', 'value']
    types = dict(_type='Type', name='str', value='Expression')

    def __str__(self):
        return '{0._type} {0.name} = {0.value};'.format(self)


class ArrayDef(Statement):
    children = ['_type', 'size', 'name']
    types = dict(_type='Type', size='Expression', name='str')

    def __str__(self):
        return '{0._type.base}[{0.size}] {0.name};'.format(self)


class ExprStatement(Statement):
    children = ['expr']
    types = dict(expr='Expression')

    def __str__(self):
        return str(self.expr) + ';'


class Expression(Node):
    __metaclass__ = ABCMeta


class Reference:
    __metaclass__ = ABCMeta


class VarUse(Expression, Reference):
    children = ['name', 'index']
    types = dict(name='str', index='Expression?')

    def __str__(self):
        if self.index is not None:
            return '{0.name}[{0.index}]'.format(self)
        return self.name


class Index(Expression, Reference):
    children = ['base', 'index']
    types = dict(base='Expression', index='Expression')

    def __str__(self):
        return '{0.base}[{0.index}]'.format(self)


class BinaryOp(Expression):
    children = ['lhs', 'op', 'rhs']
    types = dict(lhs='Expression', op='Operator', rhs='Expression')

    def __str__(self):
        return '({0.lhs} {0.op} {0.rhs})'.format(self)


class UnaryOp(Expression):
    children = ['op', 'value']
    types = dict(op='Operator', value='Expression')

    def __str__(self):
        return '{0.op}{0.value}'.format(self)


class FunCall(Expression):
    children = ['name', 'args']
    types = dict(name='str', args='Expression*')

    def __str__(self):
        return '%s(%s)' % (self.name, ', '.join(map(str, self.args)))


class Const(Expression):
    __metaclass__ = ABCMeta


class BoolConst(Const):
    children = ['value']
    types = dict(value='bool')

    def __str__(self):
        return 'true' if self.value else 'false'


class CharConst(Const):
    children = ['value']
    types = dict(value='str')

    def __str__(self):
        return '\'' + StringConst.escape(self.value).replace('\'', '\\\'') + '\''


class IntConst(Const):
    children = ['value']
    types = dict(value='int')

    def __str__(self):
        return str(self.value)


class HexConst(IntConst):
    def __str__(self):
        return hex(self.value)


class StringConst(Const):
    children = ['value']
    types = dict(value='str')

    def __str__(self):
        return '"' + self.escape(self.value).replace('"', r'\"') + '"'

    trans = str.maketrans({
        '\n': r'\n',
        '\t': r'\t',
        '\v': r'\v',
        '\b': r'\b',
        '\r': r'\r',
        '\f': r'\f',
        '\a': r'\a',
        '\\': r'\\',
        '\0': r'\0'
    })

    @classmethod
    def escape(cls, s):
        return s.translate(cls.trans)


class DeleteNode(Node):
    '''
    This is a special type of node that can be returned by an
    `util.ASTTransformer` method in order to remove an AST node from the tree.
    '''
    pass
