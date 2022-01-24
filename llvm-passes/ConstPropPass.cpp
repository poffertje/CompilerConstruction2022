/*
 * Dummy (and minimal) function pass to serve as a starting point for your
 * Assignment 2 passes. It simply visits every function and prints every call
 * instruction it finds.
 */

#define DEBUG_TYPE "ConstPropPass"
#include "utils.h"

namespace {

    enum Operations {
        Add,
        Sub,
        Mul,
        Shl,
        AShr,
        Unknown
    };

    Operations opcodeToOperations(int opcode) {
        switch(opcode) {
            case 13: return Add;
            case 15: return Sub;
            case 17: return Mul;
            case 25: return Shl;
            case 27: return AShr;
            default: return Unknown;
        }
    }

    class ConstPropPass : public FunctionPass {
    public:
        static char ID;

        ConstPropPass() : FunctionPass(ID) {}
        virtual bool runOnFunction(Function &f) override;
    private:
        template<class constType>
        void constFold(Instruction *i, Operations oper);

        void constFoldInt(Instruction *i);

        Constant* createConstant(Instruction *i, Operations oper);
    };
}

bool ConstPropPass::runOnFunction(Function &f) {

    for (BasicBlock &bb : f) {
        LOG_LINE("Entering basic block: " << bb);
        for (Instruction &i : bb) {
            LOG_LINE("Checking instruction: " << i);
            constFoldInt(&i);
        }
    }

    return true;  // We did not alter the IR
}

template<class constType>
void ConstPropPass::constFold(Instruction *i, Operations oper) {
    bool constants = true;
    SmallVector<User *, 32> replaceable;

    for (Use &u : i->operands()) {
        Value *v = u.get();
        constants &= isa<constType>(v);
    }
    if(constants) {
        LOG_LINE("This operation is constant");

        Constant *c = createConstant(i, oper);
        LOG_LINE("Got constant: " << *c);
        
        // Find all users
        for(User *u : i->users()) {
            LOG_LINE("User: " << *u);
            replaceable.push_back(u);
        }

        // Replace with constant
        for(User *u : replaceable) {
            u->replaceUsesOfWith(i, c);
        }
    }
}

#define _BINARY_OP_CONST_CREATE__infix(constType, operator)\
    BinaryOperator *op = cast<BinaryOperator>(i);         \
    ConstantInt *a = cast<constType>(op->getOperand(0));  \
    ConstantInt *b = cast<constType>(op->getOperand(1));  \
    APInt cVal = a->getValue() operator b->getValue();    \
    Constant *c = constType::get(a->getType(), cVal);     \
    return c;

#define _BINARY_OP_CONST_CREATE__fun(constType, fun)      \
    BinaryOperator *op = cast<BinaryOperator>(i);         \
    ConstantInt *a = cast<constType>(op->getOperand(0));  \
    ConstantInt *b = cast<constType>(op->getOperand(1));  \
    APInt cVal = a->getValue().fun(b->getValue());        \
    Constant *c = constType::get(a->getType(), cVal);     \
    return c;

Constant* ConstPropPass::createConstant(Instruction *i, Operations oper) {
    switch(oper) {
        case Add: {
            _BINARY_OP_CONST_CREATE__infix(ConstantInt, +)
        }
        case Sub: {
            _BINARY_OP_CONST_CREATE__infix(ConstantInt, -)
        }
        case Mul: {
            _BINARY_OP_CONST_CREATE__infix(ConstantInt, *)
        }
        case AShr: {
            _BINARY_OP_CONST_CREATE__fun(ConstantInt, ashr)
        }
        case Shl: {
            _BINARY_OP_CONST_CREATE__fun(ConstantInt, shl)
        }
        default:
            return NULL;
    }
}

void ConstPropPass::constFoldInt(Instruction *i) {
    if(BinaryOperator* op = dyn_cast<BinaryOperator>(i)) {
        Instruction::BinaryOps opcode = op->getOpcode();
        Operations oper = opcodeToOperations(opcode);
        if(oper == Add || oper == Sub || oper == Mul || oper == Shl || oper == AShr) {
            constFold<ConstantInt>(i, oper);
        }
    }
}

// Register the pass with LLVM so we can invoke it with opt. The first argument
// to RegisterPass is the commandline switch to run this pass (e.g., opt
// -coco-ConstPropPass, the second argument is a description shown in the help text
// about this pass.
char ConstPropPass::ID = 0;
static RegisterPass<ConstPropPass> X("coco-constprop", "Example LLVM pass printing each function it visits, and every call instruction it finds");
