/*
 * Dummy loop pass to serve as a starting point for your Assignment 2 passes.
 * It goes through every basicblock in each loop and checks that every block
 * inside the loop is dominated by the header (which should always be the case).
 * For an example of a function pass, see DummyPass.cpp.
 */

#define DEBUG_TYPE "DummyDTPass"
#include "utils.h"

namespace {
    class DummyDTPass : public LoopPass {
    public:
        static char ID;
        DummyDTPass() : LoopPass(ID) {}
        virtual bool runOnLoop(Loop *L, LPPassManager &LPM) override;
        void getAnalysisUsage(AnalysisUsage &AU) const override;
    };
}

void DummyDTPass::getAnalysisUsage(AnalysisUsage &AU) const {
    // Tell LLVM we need some analysis info which we use for analyzing the
    // DominatorTree.
    AU.setPreservesCFG();
    AU.addRequired<LoopInfoWrapperPass>();
    getLoopAnalysisUsage(AU);
}

bool DummyDTPass::runOnLoop(Loop *L, LPPassManager &LPM) {
    BasicBlock *Header = L->getHeader();
    DominatorTree *DT = &getAnalysis<DominatorTreeWrapperPass>().getDomTree();

    for (BasicBlock *BB : L->blocks()) {
        if (DT->dominates(Header, BB)) {
            LOG_LINE("The loop header dominates this Basic Block");
        } else {
            LOG_LINE("There is something terribly wrong with " << *BB);
        }
    }

    return false;
}

char DummyDTPass::ID = 0;
RegisterPass<DummyDTPass> X("coco-dummydtpass", "CoCo Dominator Tree Example");
