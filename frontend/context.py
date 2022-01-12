from util import ASTVisitor, NodeError, BackrefError


class ContextAnalysis(ASTVisitor):
    '''
    This traversal implements the scoping rules from the Language Reference.
    `add_to_scope` and `find_in_scope` implement the stack structure of scoping
    levels.
    '''

    def add_to_scope(self, node):
        curscope = self.scopes[-1]

        if node.name in curscope:
            raise BackrefError(
                    node.location, 'Error: redefinition of %s' % node.name,
                    curscope[node.name].location, 'Note: defined earlier here')

        curscope[node.name] = node
        #print('scope[%s] = %s' % (node.name, repr(node)))

    def find_in_scope(self, node):
        for scope in reversed(self.scopes):
            if node.name in scope:
                #print('%s -> %s' % (node.name, repr(scope[node.name])))
                node.definition = scope[node.name]
                return

        raise NodeError(node, 'Error: %s is undefined' % node.name)

    def visitProgram(self, node):
        self.scopes = [{}]
        self.fundefs = []

        # collect globals
        self.visit_children(node)

        # visit function bodies after collecting all functions and globals so
        # that their names are in the global scope
        for fundef in self.fundefs:
            self.scopes.append({})
            # put function name and parameters in the same scope as local vars so
            # that they cannot shadow each other
            self.add_to_scope(fundef)
            self.visit(fundef._type.params)
            self.visit(fundef.body.statements)
            self.scopes.pop()

    def visitGlobalDec(self, node):
        self.add_to_scope(node)

    def visitGlobalDef(self, node):
        self.visit_children(node)
        self.add_to_scope(node)

    def visitFunDec(self, node):
        self.add_to_scope(node)

    def visitFunDef(self, node):
        # don't traverse into function bodies, `visitProgram` does that after
        # collecting all globals first
        self.add_to_scope(node)
        self.fundefs.append(node)

    def visitBlock(self, node):
        # start a new scope for each block
        self.scopes.append({})
        self.visit_children(node)
        self.scopes.pop()

    def visitParam(self, node):
        self.add_to_scope(node)

    def visitVarDef(self, node):
        self.visit_children(node)
        self.add_to_scope(node)

    def visitArrayDef(self, node):
        self.visit_children(node)
        self.add_to_scope(node)

    def visitVarUse(self, node):
        self.find_in_scope(node)
        self.visit_children(node)

    def visitFunCall(self, node):
        self.find_in_scope(node)
        self.visit_children(node)
