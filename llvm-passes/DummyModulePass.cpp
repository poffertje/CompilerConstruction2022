/*
 * Dummy module pass which can be used as example and starting point for
 * Assignment 3. This pass inserts calls to a helper function for every stack
 * allocation. The helper function prints the size of the stack allocation and
 * serves as an example how to create and insert helpers. The implementation of
 * the helper function can be found in runtime/dummy.c.
 */

#define DEBUG_TYPE "DummyModulePass"
#include "utils.h"

namespace {
    class DummyModulePass : public ModulePass {
    public:
        static char ID;
        DummyModulePass() : ModulePass(ID) {}
        virtual bool runOnModule(Module &M) override;

    private:
        Function *PrintAllocFunc;

        bool instrumentAllocations(Function &F);
    };
}

/*
 * Finds all allocations in a function and inserts a call that prints its size.
 */
bool DummyModulePass::instrumentAllocations(Function &F) {
    bool Changed = false;

    // Construct an IRBuilder (at a random insertion point) so we can reuse it
    // every time we need it.
    IRBuilder<> B(&F.getEntryBlock());

    // Iterate over all instructions in this function.
    for (Instruction &II : instructions(F)) {
        Instruction *I = &II;

        // To see if this instruction is an allocation, we try to cast it to an
        // AllocaInst. This returns a nullptr if this instruction is not an
        // AllocaInst.
        if (AllocaInst *AI = dyn_cast<AllocaInst>(I)) {
            // Create a new call to our helper function, with the number of
            // allocated elements as argument.
            B.SetInsertPoint(AI);
            B.CreateCall(PrintAllocFunc, { AI->getArraySize() });
            Changed = true;
        }
    }
    return Changed;
}

bool DummyModulePass::runOnModule(Module &M) {
    // Retrieve a pointer to the helper function. The instrumentAllocations
    // function will insert calls to this function for every allocation. This
    // function is written in our runtime (runtime/dummy.c). To see its (LLVM)
    // type, you can check runtime/obj/dummy.ll)
    LLVMContext &C = M.getContext();
    Type *VoidTy = Type::getVoidTy(C);
    Type *Int32Ty = Type::getInt32Ty(C);
    //   void @__coco_dummy_print_allocation(i32 %elems)
    auto FnCallee = M.getOrInsertFunction("__coco_dummy_print_allocation",
                                          VoidTy, Int32Ty);
    PrintAllocFunc = cast<Function>(FnCallee.getCallee());

    // LLVM wants to know whether we made any modifications to the IR, so we
    // keep track of this.
    bool Changed = false;

    for (Function &F : M) {
        // We want to skip instrumenting certain functions, like declarations
        // and helper functions (e.g., our dummy_print_allocation)
        if (!shouldInstrument(&F))
            continue;

        LOG_LINE("Visiting function " << F.getName());
        Changed |= instrumentAllocations(F);
    }

    return Changed;
}

// Register the pass with LLVM so we can invoke it with opt. The first argument
// to RegisterPass is the commandline switch to run this pass (e.g., opt
// -coco-dummymodulepass, the second argument is a description shown in the help
// text about this pass.
char DummyModulePass::ID = 0;
static RegisterPass<DummyModulePass> X("coco-dummymodulepass", "Example LLVM module pass that inserts prints for every allocation.");
