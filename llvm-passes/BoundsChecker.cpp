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
        Value* getPointerOffset(GetElementP &F);

        bool instrumentGEPs(Function &F);
    };
}

bool BoundsChecker::instrumentGEPs(Function &F) {
    for (Instruction &II : instructions(F)) {
        if(GetElementPtrInst* GEP = dyn_cast<GetElementPtrInst>(&II)) {
            LOG_LINE("Got a GEP:  " << GEP);
            getPointerOffset(*GEP);
        }
    }
    return false;
}

bool BoundsChecker::runOnModule(Module &M) {
    // Retrieve a pointer to the helper function. The instrumentAllocations
    // function will insert calls to this function for every allocation. This
    // function is written in our runtime (runtime/dummy.c). To see its (LLVM)
    // type, you can check runtime/obj/dummy.ll)

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

    return Changed;
}

Value* getPointerOffset(GetElementPtrInst &GEP) {
    unsigned width = llvm::DataLayout::getIndexTypeSizeInBits(GEP.getType());
    if (GEP.accumulateConstantOffset()) {

    } else {
        
    }
}

// Register the pass with LLVM so we can invoke it with opt. The first argument
// to RegisterPass is the commandline switch to run this pass (e.g., opt
// -coco-BoundsChecker, the second argument is a description shown in the help
// text about this pass.
char BoundsChecker::ID = 0;
static RegisterPass<BoundsChecker> X("coco-boundscheck", "Example LLVM module pass that inserts prints for every allocation.");
