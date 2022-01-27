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
        DataLayout *dl;

        Value *getPointerOffset(GetElementPtrInst *GEP, IRBuilder<> *B, SmallDenseMap<GetElementPtrInst*, Value*, 32> *computedOffsets);
        Value *getPtrOrigin(GetElementPtrInst *GEP);
        Value *getPtrSize(Value *origin);
        bool instrumentGEPs(Function &F);
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
        if(GetElementPtrInst* GEP = dyn_cast<GetElementPtrInst>(&II)) {
            LOG_LINE("Got a GEP:  " << *GEP);
            Value* offset = getPointerOffset(GEP, &B, &computedOffsets);
            LOG_LINE("Got offset: " << *offset);
            Value* origin = getPtrOrigin(GEP);
            LOG_LINE("Got origin: " << *origin);
            Value* originSize = getPtrSize(origin);
            LOG_LINE("Origin size: " << *originSize);
            modified = true;
        }
    }
    return modified;
}

bool BoundsChecker::runOnModule(Module &M) {
    // Retrieve a pointer to the helper function. The instrumentAllocations
    // function will insert calls to this function for every allocation. This
    // function is written in our runtime (runtime/dummy.c). To see its (LLVM)
    // type, you can check runtime/obj/dummy.ll)

    dl = new DataLayout(&M);

    // LLVM wants to know whether we made any modifications to the IR, so we
    // keep track of this.
    bool Changed = false;

    for (Function &F : M) {
        // We want to skip instrumenting certain functions, like declarations
        // and helper functions (e.g., our dummy_print_allocation)
        if (!shouldInstrument(&F))
            continue;

        LOG_LINE("Visiting function " << F.getName());
        instrumentGEPs(F);
    }

    delete dl;
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

Value* BoundsChecker::getPtrOrigin(GetElementPtrInst *GEP) {
    Value* ptr = GEP->getOperand(0);
    if(GetElementPtrInst *GEP2 = dyn_cast<GetElementPtrInst>(ptr)) {
        return getPtrOrigin(GEP2);
    } else {
        return ptr;
    }
}

Value* BoundsChecker::getPtrSize(Value* origin) {
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
    }
    ERROR("Unknown origin type");
}

// Register the pass with LLVM so we can invoke it with opt. The first argument
// to RegisterPass is the commandline switch to run this pass (e.g., opt
// -coco-BoundsChecker, the second argument is a description shown in the help
// text about this pass.
char BoundsChecker::ID = 0;
static RegisterPass<BoundsChecker> X("coco-boundscheck", "Example LLVM module pass that inserts prints for every allocation.");
