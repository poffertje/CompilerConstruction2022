/*
 * Dummy module pass which can be used as example and starting point for
 * Assignment 3. This pass inserts calls to a helper function for every stack
 * allocation. The helper function prints the size of the stack allocation and
 * serves as an example how to create and insert helpers. The implementation of
 * the helper function can be found in runtime/dummy.c.
 */

#define DEBUG_TYPE "BoundsChecker"
#include "utils.h"

namespace {
    class BoundsChecker : public ModulePass {
    public:
        static char ID;
        BoundsChecker() : ModulePass(ID) {}
        virtual bool runOnModule(Module &M) override;

    private:
        Function *BoundscheckFunc;

        Value *getPointerOffset(GetElementPtrInst *GEP, IRBuilder<> *B, SmallDenseMap<GetElementPtrInst*, Value*, 32> *computedOffsets);
        Value *getPtrOrigin(Value *ptr);
        Value *getOriginSize(Value *origin);
        bool isBoundscheckRequired(GetElementPtrInst *GEP);
        bool tryCloneFunctions(Module &M);
        Function* cloneFunction(Function &F, SmallVectorImpl<Argument*> &pointerArgs);
        void replaceCallInsts(Function &F, Function *cloneFunc, SmallVectorImpl<Function*> &originalFunctions);
        bool instrumentGEPs(Function &F);
        bool shouldClone(Function &F, SmallVectorImpl<Argument*> &pointerArgs);
        Argument* findArgumentByName(Function &F, std::string name);
    };

    ConstantInt *sumConstantInts(ConstantInt *a, ConstantInt *b) {
        APInt cVal = a->getValue() + b->getValue();
        Constant *c = ConstantInt::get(a->getType(), cVal);
        return cast<ConstantInt>(c);
    }
}

bool BoundsChecker::instrumentGEPs(Function &F) {
    // Construct an IRBuilder (at a random insertion point) so we can reuse it
    // every time we need it.
    IRBuilder<> B(&F.getEntryBlock());
    SmallDenseMap<GetElementPtrInst*, Value*, 32> computedOffsets;

    bool modified = false;

    for (Instruction &II : instructions(F)) {
        GetElementPtrInst* GEP = dyn_cast<GetElementPtrInst>(&II);
        if(GEP && isBoundscheckRequired(GEP)) {
            LOG_LINE("Got a GEP:  " << *GEP);
            Value* offset = getPointerOffset(GEP, &B, &computedOffsets);
            LOG_LINE("Got offset: " << *offset);
            Value* origin = getPtrOrigin(GEP);
            LOG_LINE("Got origin: " << *origin);
            Value* originSize = getOriginSize(origin);
            LOG_LINE("Origin size: " << *originSize);

            // Insert bounds check
            B.SetInsertPoint(GEP);
            B.CreateCall(BoundscheckFunc, {offset, originSize});
            modified = true;
        }
    }
    return modified;
}

bool BoundsChecker::runOnModule(Module &M) {
    // Retrieve a pointer to the helper function.
    LLVMContext &C = M.getContext();
    Type *VoidTy = Type::getVoidTy(C);
    Type *Int32Ty = Type::getInt32Ty(C);
    auto FnCallee = M.getOrInsertFunction("__coco_check_bounds",
                                          VoidTy, Int32Ty, Int32Ty);
    BoundscheckFunc = cast<Function>(FnCallee.getCallee());

    // LLVM wants to know whether we made any modifications to the IR, so we
    // keep track of this.
    bool Changed = false;

    tryCloneFunctions(M);

    LOG_LINE("Module: " << M);

    for (Function &F : M) {
        // We want to skip instrumenting certain functions, like declarations
        // and helper functions (e.g., our dummy_print_allocation)
        if (!shouldInstrument(&F))
            continue;

        LOG_LINE("Visiting function " << F.getName());
        instrumentGEPs(F);
    }

    return Changed;
}

Value* BoundsChecker::getPointerOffset(GetElementPtrInst *GEP, IRBuilder<> *B, SmallDenseMap<GetElementPtrInst*, Value*, 32> *computedOffsets) {
    if(computedOffsets->count(GEP) == 1) {
        return computedOffsets->lookup(GEP);
    }
    
    Value* ptr = GEP->getOperand(0);
    Value* off = GEP->getOperand(1);

    if (GetElementPtrInst *GEP2 = dyn_cast<GetElementPtrInst>(ptr)) {
        Value* off2 = getPointerOffset(GEP2, B, computedOffsets);
        ConstantInt *c_off = dyn_cast<ConstantInt>(off);
        ConstantInt *c_off2 = dyn_cast<ConstantInt>(off2);

        if(c_off && c_off2) {
            ConstantInt *calculated = sumConstantInts(c_off, c_off2);
            computedOffsets->insert({GEP, calculated});
            return calculated;
        } else {
            LOG_LINE("Creating ADD instruction");
            B->SetInsertPoint(GEP);
            Value *inserted = B->CreateAdd(off, off2);
            computedOffsets->insert({GEP, inserted});
            return inserted;
        }
    } else {
        computedOffsets->insert({GEP, off});
        return off;
    }
}

Value* BoundsChecker::getPtrOrigin(Value* ptr) {
    if(GetElementPtrInst *GEP = dyn_cast<GetElementPtrInst>(ptr)) {
        return getPtrOrigin(GEP->getOperand(0));
    } else {
        return ptr;
    }
}

Value* BoundsChecker::getOriginSize(Value* origin) {
    if(AllocaInst *a_inst = dyn_cast<AllocaInst>(origin)) {
        return a_inst->getArraySize();
    } else if(Constant *c_origin = dyn_cast<Constant>(origin)) {
        if(PointerType *pt = dyn_cast<PointerType>(c_origin->getType())) {
            Type* ptrElemTy = pt->getPointerElementType();
            if(SequentialType* seq = dyn_cast<SequentialType>(ptrElemTy)) {
                Value* ret = ConstantInt::get(IntegerType::getInt32Ty(origin->getContext()), seq->getNumElements());
                return ret;
            } else {
                ERROR("Something has PointerType but it does not refer to a SequentialType");
            }
        } else {
            ERROR("Something is a Constant but it has not a PointerType");
        }
    } else if(Argument *arg_origin = dyn_cast<Argument>(origin)) {
        Function *f = arg_origin->getParent();
        LOG_LINE("Name: " << f->getName());
        if (f->getName().equals("main")) {
            LOG_LINE("This function is called main");
            return f->getArg(0);
        }

        Argument* arg_size = findArgumentByName(*f, arg_origin->getName().str() + "_coco_size");
        if(!arg_size) {
            ERROR("Cannot find argument size for " << *arg_origin);
        }
        return arg_size;
    }
    ERROR("Unknown origin type");
}

Argument* BoundsChecker::findArgumentByName(Function &F, std::string name) {
    for(Argument &arg : F.args()) {
        if(arg.getName().equals(name)) {
            return &arg;
        }
    }
    return NULL;
}

bool BoundsChecker::isBoundscheckRequired(GetElementPtrInst *GEP) {
    return GEP->getNumIndices() == 1;
}

bool BoundsChecker::tryCloneFunctions(Module &M) {
    LOG_LINE("Performing cloning");
    SmallVector<Function*, 16> cloneFunctions;
    SmallVector<Function*, 16> originalFunctions;

    for(Function &F : M) {
        if(shouldInstrument(&F)) {
            LOG_LINE("Checking function " << F);
            SmallVector<Argument*, 8> pointerArgs;
            if(shouldClone(F, pointerArgs)) {
                LOG_LINE("Should clone");
                Function* cloneFunc = cloneFunction(F, pointerArgs);
                cloneFunctions.push_back(cloneFunc);
                originalFunctions.push_back(&F);
            }
        }
    }

    for(size_t i = 0; i < cloneFunctions.size(); i++) {
        Function* cloneFunc = cloneFunctions[i];
        Function* origFunc = originalFunctions[i];

        replaceCallInsts(*origFunc, cloneFunc, originalFunctions);
    }

    LOG_LINE("Deleting functions");

    for(Function* F : originalFunctions) {
        F->dropAllReferences();
        F->eraseFromParent();
    }
    
    return false;
}

Function* BoundsChecker::cloneFunction(Function &F, SmallVectorImpl<Argument*> &pointerArgs) {
    // Clone function with new arguments (sizes of the various arrays)
    Type* Int32Ty = Type::getInt32Ty(F.getContext());
    Type* newParamTypes[pointerArgs.size()];
    std::fill_n(newParamTypes, pointerArgs.size(), Int32Ty);
    SmallVector<Argument*, 8> newArgs;
    Function* cloneFunc = addParamsToFunction(&F, ArrayRef<Type*>(newParamTypes, pointerArgs.size()), newArgs);

    // Change new arguments names
    for(size_t i = 0; i < newArgs.size(); ++i) {
        newArgs[i]->setName(pointerArgs[i]->getName() + "_coco_size");
    }

    LOG_LINE("Clone func " << *cloneFunc);

    //replaceCallInsts(F, cloneFunc);
    return cloneFunc;
}

void BoundsChecker::replaceCallInsts(Function &F, Function *cloneFunc, SmallVectorImpl<Function*> &originalFunctions) {
    for(User* u : F.users()) {
        LOG_LINE("User: " << *u);
        if(CallInst* oldCall = dyn_cast<CallInst>(u)) {
            // If this call instruction is inside an original function (one which will be removed)
            // then we don't want to do anything
            for(Function* origFunc : originalFunctions) {
                if(oldCall->getCaller() == origFunc) {
                    return;
                }
            }

            SmallVector<Value*, 8> newArgs;
            SmallVector<Value*, 8> ptrArgsSizes;
            // Find all arguments and sizes of pointer arguments
            for(Value* arg_operand : oldCall->arg_operands()) {
                LOG_LINE("arg operand: " << *arg_operand);
                newArgs.push_back(arg_operand);
                if(arg_operand->getType()->isPointerTy()) {
                    Value* origin = getPtrOrigin(arg_operand);
                    Value* origin_size = getOriginSize(origin);
                    LOG_LINE("origin: " << *origin);
                    LOG_LINE("origin size: " << *origin_size);
                    ptrArgsSizes.push_back(origin_size);
                }
            }
            // Push sizes of pointer arguments as new arguments at the end
            for(Value* argSize : ptrArgsSizes) {
                newArgs.push_back(argSize);
            }

            ReplaceInstWithInst(oldCall, CallInst::Create(cloneFunc, newArgs));
        }
    }
}

bool BoundsChecker::shouldClone(Function &F, SmallVectorImpl<Argument*> &pointerArgs) {
    if(F.getName().equals("main")) {
        return false;
    }

    for(Argument &arg : F.args()) {
        Type* ty = arg.getType();
        if(ty->isPointerTy()) {
            pointerArgs.push_back(&arg);
        }
    }
    return pointerArgs.size() > 0;
}

// Register the pass with LLVM so we can invoke it with opt. The first argument
// to RegisterPass is the commandline switch to run this pass (e.g., opt
// -coco-BoundsChecker, the second argument is a description shown in the help
// text about this pass.
char BoundsChecker::ID = 0;
static RegisterPass<BoundsChecker> X("coco-boundscheck", "Example LLVM module pass that inserts prints for every allocation.");
