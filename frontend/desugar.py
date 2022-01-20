from util import ASTTransformer
from ast import Type, Operator, VarDef, ArrayDef, Assignment, Modification, \
        If, Block, VarUse, BinaryOp, IntConst, Return, While, For


class Desugarer(ASTTransformer):
    def __init__(self):
        self.varcache_stack = [{}]

    def makevar(self, name):
        # Generate a variable starting with an underscore (which is not allowed
        # in the language itself, so should be unique). To make the variable
        # unique, add a counter value if there are multiple generated variables
        # of the same name within the current scope.
        # A variable can be tagged as 'ssa' which means it is only assigned once
        # at its definition.
        name = '_' + name
        varcache = self.varcache_stack[-1]
        occurrences = varcache.setdefault(name, 0)
        varcache[name] += 1
        return name if not occurrences else name + str(occurrences + 1)

    def visitFunDef(self, node):
        self.varcache_stack.append({})
        self.visit_children(node)
        self.varcache_stack.pop()

    def visitModification(self, m):
        # from: lhs op= rhs
        # to:   lhs = lhs op rhs
        self.visit_children(m)
        return Assignment(m.ref, BinaryOp(m.ref, m.op, m.value)).at(m)
        
    def visitFor(self, f):
        '''
        from:   for (type id = init to end) {
                    ...
                }
                
        to:     {
                    type id = init;
                    while (id < end) {
                        ...
                        id += 1
                    }
                }
        '''
        
        assert isinstance(f.loopbody, Block)
        assert str(f.vartype) == "int"
        
        self.visit_children(f)
        
        ref = VarUse(f.varname)
        whilebody = Block(f.loopbody.statements + [self.visitModification(Modification(ref, Operator.get('+'), IntConst(1)))])
        whilecond = BinaryOp(ref, Operator.get('<'), f.to)
        whileblock = While(whilecond, whilebody, False)
        # update the iter property of the AST node to distinguish between while and for loops
        whileblock.set_iter(ref)

        return Block([
            VarDef(f.vartype, f.varname, f._from),
            whileblock
        ])
