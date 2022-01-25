/*
 * Dummy (and minimal) function pass to serve as a starting point for your
 * Assignment 2 passes. It simply visits every function and prints every call
 * instruction it finds.
 */

#define DEBUG_TYPE "ConstPropPass"
#include "utils.h"

namespace {

    enum Operation {
        Add,
        FAdd,
        Sub,
        FSub,
        Mul,
        FMul,
        UDiv,
        SDiv,
        FDiv,
        URem,
        SRem,
        FRem,
        Shl,
        LShr,
        AShr,
        Unknown
    };

    Operation opcodeToOperation(int opcode) {
        switch(opcode) {
            case 13: return Add;
            case 14: return FAdd;
            case 15: return Sub;
            case 16: return FSub;
            case 17: return Mul;
            case 18: return FMul;
            case 19: return UDiv;
            case 20: return SDiv;
            case 21: return FDiv;
            case 22: return URem;
            case 23: return SRem;
            case 24: return FRem;
            case 25: return Shl;
            case 26: return LShr;
            case 27: return AShr;
            default: return Unknown;
        }
    }

    bool isRightOperandZero(Instruction *i) {
        BinaryOperator *op = cast<BinaryOperator>(i);
        return cast<Constant>(op->getOperand(1))->isZeroValue();
    }

    class ConstPropPass : public FunctionPass {
    public:
        static char ID;

        ConstPropPass() : FunctionPass(ID) {}
        virtual bool runOnFunction(Function &f) override;
    private:

        Function *curF = NULL;

        template<class constType>
        bool constFold(Instruction *i, Operation oper);

        bool constFoldInt(Instruction *i);
        bool constFoldFloat(Instruction *i);

        Constant* createConstant(Instruction *i, Operation oper);
        Value* trySimplify(Instruction *i, Operation oper);
    };
}

bool ConstPropPass::runOnFunction(Function &f) {
    bool modified = false;
    for (BasicBlock &bb : f) {
        LOG_LINE("Entering basic block: " << bb);
        for (Instruction &i : bb) {
            LOG_LINE("Checking instruction: " << i);
            if(constFoldInt(&i) || constFoldFloat(&i)) {
                modified = true;
            }
        }
    }

    return modified;
}

template<class constType>
bool ConstPropPass::constFold(Instruction *i, Operation oper) {
    bool allConstants = true;
    bool someConstant = false;
    SmallVector<User *, 32> replaceable;

    for (Use &u : i->operands()) {
        Value *v = u.get();
        allConstants &= isa<constType>(v);
        someConstant |= isa<constType>(v);
    }

    Value *c = NULL;
    if(allConstants) {
        LOG_LINE("This operation is constant");

        c = createConstant(i, oper);
        if(c)
            LOG_LINE("Got constant: " << *c);
    } else if(someConstant) {
        LOG_LINE("Checking simplification");
        c = trySimplify(i, oper);
        if(c)
            LOG_LINE("Simiplified value: " << *c);
    }

    if(c) {
        // Find all users
        for(User *u : i->users()) {
            LOG_LINE("User: " << *u);
            replaceable.push_back(u);
        }

        // Replace with constant
        for(User *u : replaceable) {
            u->replaceUsesOfWith(i, c);
        }
        return replaceable.size() > 0;
    }
    return false;
}

// These macros are used so that we don't have to duplicate the same operations for every case and constant type (ConstantInt, ConstantFP, ecc...)

#define _BINARY_OP_CONST_CREATE__infix(constType, apType, getValueFun, operator)\
    BinaryOperator *op = cast<BinaryOperator>(i);                               \
    constType *a = cast<constType>(op->getOperand(0));                          \
    constType *b = cast<constType>(op->getOperand(1));                          \
    apType cVal = a->getValueFun() operator b->getValueFun();                   \
    Constant *c = constType::get(a->getType(), cVal);                           \
    return c;

#define _BINARY_OP_CONST_CREATE__fun(constType, apType, getValueFun, fun)       \
    BinaryOperator *op = cast<BinaryOperator>(i);                               \
    constType *a = cast<constType>(op->getOperand(0));                          \
    constType *b = cast<constType>(op->getOperand(1));                          \
    apType cVal = a->getValueFun().fun(b->getValueFun());                       \
    Constant *c = constType::get(a->getType(), cVal);                           \
    return c;

#define INT_BINARY_OP_CONST_CREATE__infix(operator)                  \
    _BINARY_OP_CONST_CREATE__infix(ConstantInt, APInt, getValue, operator)

#define INT_BINARY_OP_CONST_CREATE__fun(fun)                         \
    _BINARY_OP_CONST_CREATE__fun(ConstantInt, APInt, getValue, fun)

#define FLOAT_BINARY_OP_CONST_CREATE__infix(operator)                \
    _BINARY_OP_CONST_CREATE__infix(ConstantFP, APFloat, getValueAPF, operator)

#define FLOAT_BINARY_OP_CONST_CREATE__fun(fun)                       \
    _BINARY_OP_CONST_CREATE__fun(ConstantFP, APFloat, getValueAPF, fun)

Constant* ConstPropPass::createConstant(Instruction *i, Operation oper) {
    switch(oper) {
        // Integer operations
        case Add: {
            INT_BINARY_OP_CONST_CREATE__infix(+)
        }
        case Sub: {
            INT_BINARY_OP_CONST_CREATE__infix(-)
        }
        case Mul: {
            INT_BINARY_OP_CONST_CREATE__infix(*)
        }
        case UDiv: {
            if(isRightOperandZero(i))
                return NULL;
            INT_BINARY_OP_CONST_CREATE__fun(udiv)
        }
        case SDiv: {
            if(isRightOperandZero(i))
                return NULL;
            INT_BINARY_OP_CONST_CREATE__fun(sdiv)
        }
        case URem: {
            if(isRightOperandZero(i))
                return NULL;
            INT_BINARY_OP_CONST_CREATE__fun(urem)
        }
        case SRem: {
            if(isRightOperandZero(i))
                return NULL;
            INT_BINARY_OP_CONST_CREATE__fun(srem)
        }
        case Shl: {
            INT_BINARY_OP_CONST_CREATE__fun(shl)
        }
        case LShr: {
            INT_BINARY_OP_CONST_CREATE__fun(lshr)
        }
        case AShr: {
            INT_BINARY_OP_CONST_CREATE__fun(ashr)
        }

        // Floating point operations
        case FAdd: {
            FLOAT_BINARY_OP_CONST_CREATE__infix(+)
        }
        case FSub: {
            FLOAT_BINARY_OP_CONST_CREATE__infix(-)
        }
        case FMul: {
            FLOAT_BINARY_OP_CONST_CREATE__infix(*)
        }
        case FDiv: {
            FLOAT_BINARY_OP_CONST_CREATE__infix(/)
        }
        default:
            return NULL;
    }
}

// Initialize simplifcation rules
#define RULE_INIT(constType)                          \
    constType *constVal = NULL;                       \
    if(aIsConst) {                                    \
        constVal = cast<constType>(op->getOperand(0));\
    } else {                                          \
        constVal = cast<constType>(op->getOperand(1));\
    }                                                 \
    LOG_LINE("constVal: " << *constVal);

// Symmetric simplification rule (matches regardless of order of the operands)
#define RULE_SYM(cmp, ret)                     \
    if(constVal->getValue() cmp) {             \
        LOG_LINE("matched sym rule: " << #cmp);\
        return ret;                            \
    }

// Only matches if the constant is the lvalue
#define RULE_LEFT(cmp, ret)                     \
    if(aIsConst && constVal->getValue() cmp) {  \
        LOG_LINE("matched left rule: " << #cmp);\
        return ret;                             \
    }

// Only matches if the constant is the rvalue
#define RULE_RIGHT(cmp, ret)                     \
    if(!aIsConst && constVal->getValue() cmp) {  \
        LOG_LINE("matched right rule: " << #cmp);\
        return ret;                              \
    }

// Macros adapted for floating point operations (thanks to llvm for changing function names)
#define FLOAT_RULE_SYM(cmp, ret)                    \
    if(constVal->getValueAPF() cmp) {               \
        LOG_LINE("matched sym rule: " << #cmp);     \
        return ret;                                 \
    }

#define FLOAT_RULE_LEFT(cmp, ret)                   \
    if(aIsConst && constVal->getValueAPF() cmp) {   \
        LOG_LINE("matched left rule: " << #cmp);    \
        return ret;                                 \
    }

#define FLOAT_RULE_RIGHT(cmp, ret)                  \
    if(!aIsConst && constVal->getValueAPF() cmp) {  \
        LOG_LINE("matched right rule: " << #cmp);   \
        return ret;                                 \
    }

Value* ConstPropPass::trySimplify(Instruction *i, Operation oper) {
    if(!isa<BinaryOperator>(i)) {
        return NULL;
    }

    BinaryOperator *op = cast<BinaryOperator>(i);
    bool aIsConst = true;
    Value *nonConst = op->getOperand(1);
    if(isa<Constant>(op->getOperand(1))) {
        aIsConst = false;
        nonConst = op->getOperand(0);
    }

    LOG_LINE("operator: " << static_cast<typename std::underlying_type<Operation>::type>(oper));
    LOG_LINE("nonConst: " << *nonConst);

    switch(oper) {
        case Add: {
            RULE_INIT(ConstantInt)
            RULE_SYM(== 0, nonConst)
            break;
        }
        case Sub: {
            RULE_INIT(ConstantInt)
            RULE_RIGHT(== 0, nonConst)
            break;
        }
        case Mul: {
            RULE_INIT(ConstantInt)
            RULE_SYM(== 1, nonConst)
            Value *zeroVal = ConstantInt::get(IntegerType::getInt32Ty(nonConst->getContext()), 0, true);
            RULE_SYM(== 0, zeroVal)
            break;
        }
        case UDiv: // Same as signed division
        case SDiv: {
            RULE_INIT(ConstantInt)
            RULE_RIGHT(== 1, nonConst)
            Value *zeroVal = ConstantInt::get(IntegerType::getInt32Ty(nonConst->getContext()), 0, true);
            RULE_LEFT(== 0, zeroVal)
            break;
        }
        case URem: // Same as signed reminder
        case SRem: {
            RULE_INIT(ConstantInt)
            Value *zeroVal = ConstantInt::get(IntegerType::getInt32Ty(nonConst->getContext()), 0, true);
            RULE_RIGHT(== 1, zeroVal)
            RULE_LEFT(== 0, zeroVal)
            break;
        }
        case LShr: // Same as arithmetic right shift
        case AShr: // Same as left shift
        case Shl: {
            RULE_INIT(ConstantInt)
            RULE_RIGHT(== 0, nonConst)
            Value *zeroVal = ConstantInt::get(IntegerType::getInt32Ty(nonConst->getContext()), 0, true);
            RULE_LEFT(== 0, zeroVal)
            break;
        }
        case FSub: {
            RULE_INIT(ConstantFP)
            FLOAT_RULE_RIGHT(.convertToDouble() ==  0.0, nonConst)
            break;
            
        }
        case FDiv: {
            RULE_INIT(ConstantFP)
            FLOAT_RULE_RIGHT(.convertToDouble() ==  1.0, nonConst)
            Value *zeroVal = ConstantFP::get(nonConst->getContext(), APFloat(0.0));
            FLOAT_RULE_LEFT(.convertToDouble() ==  0.0, zeroVal)
            break;
        }
        case FAdd: {
            RULE_INIT(ConstantFP)
            FLOAT_RULE_SYM(.convertToDouble() ==  0.0, nonConst)
            break;
        }
        case FMul: {
            RULE_INIT(ConstantFP)
            FLOAT_RULE_SYM(.convertToDouble() ==  1.0, nonConst)
            Value *zeroVal = ConstantFP::get(nonConst->getContext(), APFloat(0.0));
            FLOAT_RULE_SYM(.convertToDouble() ==  0.0, zeroVal)
            break;
        }

        default:
            break;
    }
    return NULL;
}

bool ConstPropPass::constFoldInt(Instruction *i) {
    if(BinaryOperator* op = dyn_cast<BinaryOperator>(i)) {
        Instruction::BinaryOps opcode = op->getOpcode();
        Operation oper = opcodeToOperation(opcode);
        // Check for supported operations
        if( oper == Add || oper == Sub || oper == Mul
            || oper == Shl || oper == AShr || oper == UDiv
            || oper == SDiv || oper == SRem || oper == URem
            || oper == LShr) {
            return constFold<ConstantInt>(i, oper);
        }
    }
    return false;
}

bool ConstPropPass::constFoldFloat(Instruction *i) {
    if(BinaryOperator* op = dyn_cast<BinaryOperator>(i)) {
        Instruction::BinaryOps opcode = op->getOpcode();
        Operation oper = opcodeToOperation(opcode);
        // Check for supported operations
        if(oper == FSub || oper == FAdd || oper == FDiv || oper == FMul) {
            return constFold<ConstantFP>(i, oper);
        }
    }
    return false;
}

// Register the pass with LLVM so we can invoke it with opt. The first argument
// to RegisterPass is the commandline switch to run this pass (e.g., opt
// -coco-ConstPropPass, the second argument is a description shown in the help text
// about this pass.
char ConstPropPass::ID = 0;
static RegisterPass<ConstPropPass> X("coco-constprop", "Example LLVM pass printing each function it visits, and every call instruction it finds");
