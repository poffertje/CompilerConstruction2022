from util import ASTVisitor, NodeError, BackrefError
from ast import Type, ArrayType, FunType, Block, If, Return, Const


class TypeChecker(ASTVisitor):
    '''
    This traversal check the AST for type errors and annotates expressions
    (`ast.Expr` instances) with a `ty` attribute that points to an `ast.Type`.

    After this traversal, the AST is guaranteed to be a valid program according
    to the language specification and is ready for IR generation.

    The `check_type` helper raises an error at an AST node location (with nice
    line highlighting in the error message) if the type of a node does not match
    one of the expected types.

    `operand_types` specifies the allowed types for operands of unary and binary
    operators.
    '''

    def __init__(self):
        self.tbool = Type.get('bool')
        self.tchar = Type.get('char')
        self.tint = Type.get('int')
        self.tvoid = Type.get('void')
        self.curfn = None
        self.in_loop = False

    def operand_types(self, operator):
        if operator.is_logical():
            return [self.tbool]

        if operator.is_arithmetic() or operator.is_relational():
            return [self.tchar, self.tint]

        assert operator.is_equality()
        return [self.tbool, self.tchar, self.tint]

    def check_type(self, node, *expected):
        if node.ty not in expected:
            raise NodeError(node, 'Type mismatch: expected %s, got %s',
                    '/'.join(map(str, expected)), node.ty)

    def visitGlobalDec(self, node):
        # cannot define void globals
        if str(node._type).startswith('void'):
            raise NodeError(node, 'Error: global must be non-void')

    def visitGlobalDef(self, node):
        self.visit_children(node)

        # global definitions cannot be arrays or void
        if node._type.is_array():
            raise NodeError(node, 'Error: global must have basic type')

        if node._type == self.tvoid:
            raise NodeError(node, 'Error: global must be non-void')

        # initializer must match global type
        self.check_type(node.value, node._type)

        # initializer must be constant
        if not isinstance(node.value, Const):
            raise NodeError(node.value,
                    'Error: global initializer must be constant')

    def visitFunDef(self, node):
        # functions can only return basic types
        if node._type.return_type.is_array():
            raise NodeError(node,
                    'Error: functions can only return basic type or void')

        self.curfn = node
        self.visit_children(node)
        self.curfn = None

        # a non-void function must return a value
        if node._type.return_type != self.tvoid:
            stat = node.body.statements
            if not len(stat) or not isinstance(stat[-1], Return):
                raise NodeError(node,
                        'Error: non-void function must end with return')

    def visitParam(self, node):
        # cannot define void parameters
        if str(node._type).startswith('void'):
            raise NodeError(node, 'Error: parameter must be non-void')

    def visitVarDef(self, node):
        # variables must be primitive type
        if node._type.is_array():
            raise NodeError(node, 'Error: missing size for array definition')

        # cannot define void variables
        if node._type == self.tvoid:
            raise NodeError(node, 'Error: variable must be non-void')

        # Variable initialization must match variable type
        self.visit_children(node)
        self.check_type(node.value, node._type)

    def visitArrayDef(self, node):
        # cannot define void arrays
        if node._type.base == self.tvoid:
            raise NodeError(node, 'Error: array must be non-void')

        self.visit_children(node)
        self.check_type(node.size, self.tint)

    def visitAssignment(self, node):
        self.visit_children(node)

        # functions cannot be re-assigned
        if isinstance(node.ref.ty, FunType):
            raise NodeError(node, 'Error: cannot reassign function')

        # array pointers cannot be re-assigned
        if node.ref.ty.is_array():
            raise NodeError(node, 'Error: cannot reassign array variable')

        # assigned value must match variable type
        self.check_type(node.value, node.ref.ty)

    def visitModification(self, node):
        raise NotImplementedError  # should be desugared

    def visitIf(self, node):
        # condition must be bool
        self.visit_children(node)
        self.check_type(node.cond, self.tbool)

    def visitReturn(self, node):
        # returned type must match function type
        self.visit_children(node)
        retty = self.curfn._type.return_type
        is_void = str(retty) == 'void'

        if node.value and is_void:
            raise NodeError(node.value,
                    'Error: void function must not return a value')
        elif node.value:
            self.check_type(node.value, retty)
        elif not is_void:
            raise NodeError(node,
                    'Error: non-void function must not return void')

    def visitVarUse(self, node):
        # variable uses inherit the type of their declaration
        ty = node.definition._type

        # indexed arrays produce the array base type
        if node.index:
            self.visit_children(node)

            if not ty.is_array():
                raise BackrefError(node.location,
                        'Error: cannot index non-array variable',
                        node.definition.location,
                        'Note: variable is defined here')

            ty = ty.base

        if isinstance(ty, FunType):
            raise NodeError(node, 'Error: cannot use function as variable')

        node.ty = ty

    def visitIndex(self, node):
        # array index must have int type, base must have array type
        self.visit_children(node)
        if not node.base.ty.is_array():
            raise NodeError(node.base, 'Expected array type, got %s',
                    node.base.ty)
        self.check_type(node.index, self.tint)
        node.ty = node.base.ty.base

    def visitBinaryOp(self, node):
        # operands must be legal for operand, left/right types must match
        self.visit_children(node)
        self.check_type(node.lhs, *self.operand_types(node.op))
        self.check_type(node.rhs, node.lhs.ty)

        if node.op.is_equality() or node.op.is_relational():
            node.ty = self.tbool
        else:
            node.ty = node.lhs.ty

    def visitUnaryOp(self, node):
        # operand must be legal for operand
        self.visit_children(node)
        self.check_type(node.value, *self.operand_types(node.op))
        node.ty = node.value.ty

    def visitFunCall(self, node):
        self.visit_children(node)
        funty = node.definition._type

        if not isinstance(funty, FunType):
            raise NodeError(node, 'Error: %s is not a function' % node.name)

        typed_args = node.args
        nargs = len(node.args)
        nparams = len(funty.params)
        defargs = (node.definition.location, 'Note: function is defined here')

        # number of arguments must match number of parameters in definition
        if funty.varargs:
            if nargs < nparams:
                raise BackrefError(node.location,
                        'Not enough arguments for varargs function', *defargs)

            typed_args = node.args[:len(funty.params)]

        elif nargs != nparams:
            errnode = node.args[nparams] if nargs > nparams else node
            raise BackrefError(errnode.location,
                    'Expected %d arguments, got %d' % (nparams, nargs),
                    *defargs)

        # argument types must match defined parameter types
        for arg, param in zip(typed_args, funty.params):
            self.check_type(arg, param._type)

        # resulting expression has return type of function
        node.ty = funty.return_type

    def visitBoolConst(self, node):
        node.ty = self.tbool

    def visitCharConst(self, node):
        node.ty = self.tchar

    def visitIntConst(self, node):
        node.ty = self.tint

    def visitStringConst(self, node):
        node.ty = ArrayType.get(self.tchar)
