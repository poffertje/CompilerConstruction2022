from llvmlite import ir, binding
from util import ASTTransformer
import ast


class IRGen(ASTTransformer):
    '''
    This traversal transforms an `ast.Program` into an `llvmlite.ir.Module`.

    Note that it is an `ASTTransformer` pass, so returned values replace the
    original AST nodes. This means that after you call `visit_children(node)`,
    `node.child` has been assigned the `llvmlite.ir.*` value returned by the
    corresponding `visitXXX` function.

    Always use `add_block` to create new basic blocks, rather than calling block
    creating functions from `llvmlite` directly.

    Use `self.visit` and `self.visit_before` to traverse into child nodes, using
    the latter when you have appended new blocks in which the children must be
    created (see `visitIf` for an example).
    '''

    def __init__(self, module_name):
        self.module = ir.Module(module_name)
        self.module.triple = binding.get_default_triple()
        self.module.data_layout = ''
        self.target_data = binding.create_target_data(self.module.data_layout)
        self.builder = None
        self.terminating_return = None
        self.insert_blocks = []
        self.fns = {}
        self.vars = {}
        self.nstrings = 0
        self.zero = self.getint(0)
        self.memset = None
        self.loops = []

    @classmethod
    def compile(cls, module_name, program):
        assert isinstance(program, ast.Program)
        self = cls(module_name)
        self.visit(program)
        return self.module

    def visitProgram(self, node):
        self.visit_children(node)
        return self.module

    def visitGlobalDec(self, node):
        g = ir.GlobalVariable(self.module, self.getty(node._type), node.name)
        g.linkage = 'external'
        self.vars[node] = g
        return g

    def visitGlobalDef(self, node):
        self.visit_children(node)
        g = ir.GlobalVariable(self.module, self.getty(node._type), node.name)
        g.linkage = 'internal' if node.static else 'available_externally'
        g.initializer = node.value
        self.vars[node] = g
        return g

    def visitFunDec(self, node):
        fn = ir.Function(self.module, self.visit(node._type), node.name)
        self.fns[node] = fn
        return fn

    def visitFunDef(self, node):
        # create function with entry block
        fn = ir.Function(self.module, self.visit(node._type), node.name)
        self.fns[node] = fn
        entry = fn.append_basic_block('entry')
        self.builder = ir.IRBuilder(entry)

        # add parameter names and add them to the scope, create a local alloca
        # for non-array params (i.e. those passed by value)
        for param, ref in zip(node._type.params, fn.args):
            if param._type.is_array():
                ref.name = param.name
                self.vars[param] = ref
            else:
                ref.name = 'param.' + param.name
                ty = self.getty(param._type)
                alloca = self.builder.alloca(ty, name=param.name)
                self.builder.store(ref, alloca)
                self.vars[param] = alloca

        # tag last return statement so that visitReturn will not append a block
        stat = node.body.statements
        if len(stat) and isinstance(stat[-1], ast.Return):
            self.terminating_return = stat[-1]

        # generate statements within current function
        self.visit(node.body)

        # add terminating return to void functions
        if not self.builder.block.is_terminated:
            assert str(node._type.return_type) == 'void'
            self.builder.ret_void()

        self.builder = None
        self.terminating_return = None

        return fn

    def visitFunType(self, node):
        retty = self.getty(node.return_type)
        paramtypes = [self.getty(p._type) for p in node.params]
        return ir.FunctionType(retty, paramtypes, node.varargs)

    def visitAssignment(self, node):
        if isinstance(node.ref, ast.Index):
            ptr = self.visit(node.ref.base)
            ptrname = ptr.opname + '.idx.ptr'
        else:
            assert isinstance(node.ref, ast.VarUse)
            ptr = self.vars[node.ref.definition]
            ptrname = ptr.name + '.idx'

        if node.ref.index:
            index = self.visit(node.ref.index)
            ptr = self.builder.gep(ptr, [index], False, ptrname)

        return self.builder.store(self.visit(node.value), ptr)

    def visitModification(self, node):
        raise NotImplementedError  # should be desugared

    def visitIf(self, node):
        # first add the necessary basic blocks so that we can insert jumps to
        # them, use `visit_before` to make sure that any new basic blocks added
        # for statements in the 'if' body are inserted before the 'else' body
        prefix = self.builder.block.name
        bif = self.add_block(prefix + '.if')
        if node.nobody:
            belse = self.add_block(prefix + '.else')
            bend = self.add_block(prefix + '.endif')
        else:
            belse = bend = self.add_block(prefix + '.endif')

        # insert instructions for the predicate condition before the 'if' block
        cond = self.visit_before(node.cond, bif)
        self.builder.cbranch(cond, bif, belse)

        # insert instructions for the 'if' block before the 'else' block
        self.builder.position_at_start(bif)
        self.visit_before(node.yesbody, belse)
        self.builder.branch(bend)

        # insert instructions for the 'else' block before the end block
        if node.nobody:
            self.builder.position_at_start(belse)
            self.visit_before(node.nobody, bend)
            self.builder.branch(bend)

        # go to the end block to emit further instructions
        self.builder.position_at_start(bend)

    def visitReturn(self, node):
        self.visit_children(node)

        b = self.builder
        ret = b.ret_void() if node.value is None else b.ret(node.value)

        # a `ret` instruction terminates the current block, so start a new basic
        # block to emit further instructions, unless this return is the last
        # statement in the function
        if node is not self.terminating_return:
            b.position_at_start(self.add_block('post_return'))

        return ret

    def visitVarDef(self, node):
        ty = self.getty(node._type)
        self.vars[node] = alloca = self.builder.alloca(ty, name=node.name)
        self.builder.store(self.visit(node.value), alloca)
        return alloca

    def visitArrayDef(self, node):
        ty = self.getty(node._type.base)
        size = self.visit(node.size)
        self.vars[node] = alloca = self.builder.alloca(ty, size, node.name)

        # zero-initialize using memset
        ptr = self.builder.bitcast(alloca, ir.IntType(8).as_pointer())
        zchar = self.getint(0, 8)
        elsize = self.getint(ty.get_abi_size(self.target_data))
        nbytes = self.builder.mul(size, elsize, name='nbytes')
        no = self.getint(0, 1)
        self.builder.call(self.get_memset(), [ptr, zchar, nbytes, no])

        return alloca

    def get_memset(self):
        if self.memset is None:
            args = [ir.IntType(8).as_pointer(), ir.IntType(32)]
            self.memset = self.module.declare_intrinsic('llvm.memset', args)
        return self.memset

    def visitVarUse(self, node):
        isarray = node.ty.is_array()
        self.visit_children(node)
        ptr = self.vars[node.definition]
        name = node.name

        if node.index:
            # globals have one extra pointer level, load the pointer value first
            if isinstance(ptr, ir.GlobalVariable):
                ptr = self.builder.load(ptr, node.name)

            ptr = self.builder.gep(ptr, [node.index], False, name + '.ptr')
            name += '.idx'
        elif isarray and not isinstance(ptr, ir.GlobalVariable):
            # local arrays that are used directly as parameters are alloca's,
            # they don't need an extra load inst
            return ptr

        return self.builder.load(ptr, name)

    def visitIndex(self, node):
        self.visit_children(node)
        ptr = self.builder.gep(node.base, [node.index])
        return self.builder.load(ptr)

    def visitUnaryOp(self, node):
        # logical operators don't exist in LLVM
        if node.op == '!':
            eq = ast.Operator.get('==')
            false = self.makebool(False)
            return self.visit(ast.BinaryOp(node.value, eq, false).at(node))

        if node.op == '-':
            return self.builder.neg(self.visit(node.value))

        assert node.op == '~'
        return self.builder.not_(self.visit(node.value))

    def visitBinaryOp(self, node):
        op = node.op
        b = self.builder

        # logical operators don't exist in LLVM
        if op == '&&':
            no = self.makebool(False)
            return self.lazy_conditional(node, node.lhs, node.rhs, no)

        if op == '||':
            yes = self.makebool(True)
            return self.lazy_conditional(node, node.lhs, yes, node.rhs)

        self.visit_children(node)

        if op.is_equality() or op.is_relational():
            return b.icmp_signed(op.op, node.lhs, node.rhs)

        callbacks = {
            '+': b.add, '-': b.sub, '*': b.mul, '/': b.sdiv, '%': b.srem
        }

        return callbacks[op.op](node.lhs, node.rhs)

    def lazy_conditional(self, node, cond, yesval, noval):
        b = self.builder

        byes = self.add_block('yes')
        bno = self.add_block('no')
        bend = self.add_block('endcond')

        cond = self.visit_before(cond, byes)
        b.cbranch(cond, byes, bno)

        b.position_at_start(bend)
        phi = b.phi(self.getty(node.ty))

        b.position_at_start(byes)
        yesval = self.visit_before(yesval, bno)
        b.branch(bend)
        phi.add_incoming(yesval, b.block)

        b.position_at_start(bno)
        noval = self.visit_before(noval, bend)
        b.branch(bend)
        phi.add_incoming(noval, b.block)

        b.position_at_end(bend)
        return phi

    def visitFunCall(self, node):
        self.visit_children(node)
        return self.builder.call(self.fns[node.definition], node.args)

    def visitBoolConst(self, node):
        return ir.Constant(self.getty(node.ty), node.value)

    def visitCharConst(self, node):
        return ir.Constant(self.getty(node.ty), ord(node.value))

    def visitIntConst(self, node):
        return ir.Constant(self.getty(node.ty), node.value)

    def visitStringConst(self, node):
        # name is unique, based on simple counter
        name = '.str.%d' % self.nstrings
        self.nstrings += 1

        # convert to byte array for initializer
        sbytes = bytearray(node.value + '\0', 'utf-8')

        # define string as globally initialized array
        stringty = ir.ArrayType(ir.IntType(8), len(sbytes))
        s = ir.GlobalVariable(self.module, stringty, name)
        s.initializer = ir.Constant(stringty, sbytes)

        # strings are immutable
        s.global_constant = True

        # overlapping strings may be merged
        s.unnamed_addr = True

        # return pointer to start of string (GEP gets rid of array type)
        return self.builder.gep(s, (self.zero, self.zero), True, name)

    def getty(self, ty):
        if isinstance(ty, ast.ArrayType):
            return ir.PointerType(self.getty(ty.base))

        assert isinstance(ty, ast.Type)

        if str(ty) == 'bool':
            return ir.IntType(1)

        if str(ty) == 'char':
            return ir.IntType(8)

        if str(ty) == 'int':
            return ir.IntType(ast.Type.int_bits)

        assert str(ty) == 'void'
        return ir.VoidType()

    def add_block(self, name='', before=None):
        '''
        Add a new basic block at the current insert point. The insert point is
        either set by `visit_before` or missing, in which case the block is
        appended at the end of the function.
        '''
        if not before and self.insert_blocks:
            before = self.insert_blocks[-1]

        if before:
            fn = self.builder.function
            index = fn.basic_blocks.index(before)
            return fn.insert_basic_block(index, name)

        return self.builder.append_basic_block(name)

    def visit_before(self, node, before_block):
        '''
        Visit an AST node, making sure that all created basic blocks are
        inserted before the specified block `before_block`.
        '''
        self.insert_blocks.append(before_block)
        val = self.visit(node)
        self.insert_blocks.pop()
        return val

    @staticmethod
    def getint(value, nbits=ast.Type.int_bits):
        return ir.Constant(ir.IntType(nbits), value)

    @staticmethod
    def makebool(value):
        b = ast.BoolConst(value)
        b.ty = ast.Type('bool')
        return b
