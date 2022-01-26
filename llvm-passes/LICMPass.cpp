/*
 * Dummy loop pass to serve as a starting point for your Assignment 2 passes.
 * It goes through every basicblock in each loop and checks that every block
 * inside the loop is dominated by the header (which should always be the case).
 * For an example of a function pass, see DummyPass.cpp.
 */

#define DEBUG_TYPE "LICMPass"
#include "utils.h"

namespace {
    struct InstMoveInfo {
        Loop* loop;
        LoopInfo* loopInfo;
        SmallVectorImpl<BasicBlock*>* exitBlocks;
        Instruction* inst;
        DominatorTree* dt;
        SmallVectorImpl<Instruction*>* movable;
    };

    class LICMPass : public LoopPass {
    public:
        static char ID;
        LICMPass() : LoopPass(ID) {}
        virtual bool runOnLoop(Loop *l, LPPassManager &lpm) override;
        void getAnalysisUsage(AnalysisUsage &au) const override;
    private:
        bool myIsLoopInvariant(Instruction* i, LoopInfo *li, SmallVectorImpl<Instruction*>* movable);
        bool myIsSafeToHoist(Instruction* i, DominatorTree *dt, SmallVectorImpl<BasicBlock*> *exitBlocks);
        bool canMoveInstruction(InstMoveInfo* info);
    };
}

void LICMPass::getAnalysisUsage(AnalysisUsage &au) const {
    // Tell LLVM we need some analysis info which we use for analyzing the
    // DominatorTree.
    au.setPreservesCFG();
    au.addRequired<LoopInfoWrapperPass>();
    getLoopAnalysisUsage(au);
}

bool LICMPass::runOnLoop(Loop *l, LPPassManager &lpm) {
    bool modified = false;

    BasicBlock *header = l->getHeader();
    DominatorTree *dt = &getAnalysis<DominatorTreeWrapperPass>().getDomTree();
    LoopInfo* li = &getAnalysis<LoopInfoWrapperPass>().getLoopInfo();
    SmallVector<Instruction*, 32> movable;

    SmallVector<BasicBlock*, 32> exitBlocks;
    l->getExitBlocks(exitBlocks);

    for (BasicBlock *bb : l->blocks()) {
        if (dt->dominates(header, bb)) {
            LOG_LINE("The loop header dominates this Basic Block" << *bb);
            LOG_LINE("Loop depth: " << li->getLoopDepth(bb));
            if(li->getLoopDepth(bb) == 1) {
                LOG_LINE("It is not in a sub-loop");
                for(Instruction &i : *bb) {
                    InstMoveInfo info = {l, li, &exitBlocks, &i, dt, &movable};
                    if (canMoveInstruction(&info)) {
                        movable.push_back(&i);
                    }
                }
            } else {
                LOG_LINE("It is in a sub-loop");
            }
        } else {
            LOG_LINE("There is something terribly wrong with " << *bb);
        }
    }

    BasicBlock* preheader = l->getLoopPreheader();
    if(!preheader)
        ERROR("Cannot work in a loop without preheader");
    
    for (Instruction *i : movable) {
        i->moveBefore(preheader->getTerminator());
        modified = true;
    }

    return modified;
}

bool LICMPass::canMoveInstruction(InstMoveInfo* info) {
    LOG_LINE("Instruction: " << *info->inst);
    if(myIsLoopInvariant(info->inst, info->loopInfo, info->movable)
       && myIsSafeToHoist(info->inst, info->dt, info->exitBlocks)) {
        LOG_LINE("Instruction can be moved to preheader");
        return true;
    }
    LOG_LINE("Instruction can not be moved to preheader");
    return false;
}


bool LICMPass::myIsLoopInvariant(Instruction *i, LoopInfo* li, SmallVectorImpl<Instruction*>* movable) {
    for (Use &u : i->operands()) {
        Value *v = u.get();
        LOG_LINE("Checking operand: " << *v);
        if (Instruction* opI = dyn_cast<Instruction>(v)) {
            bool movableOperand = false;
            for(Instruction *toMove : *movable) {
                if(toMove == opI) {
                    LOG_LINE("Will be moved later");
                    movableOperand = true;
                    break;
                }
            }
            if(!movableOperand && li->getLoopDepth(opI->getParent()) != 0) {
                LOG_LINE("Not outside of loop");
                return false;
            }
        } else if (!isa<Constant>(v)) {
            LOG_LINE("Not a constant");
            return false;
        }
    }
    
    return i->isBinaryOp() || i->isShift() || isa<SelectInst>(i) || isa<CastInst>(i) || isa<GetElementPtrInst>(i);

}

bool LICMPass::myIsSafeToHoist(Instruction *i, DominatorTree *dt, SmallVectorImpl<BasicBlock*> *exitBlocks) {
    bool dominatesExitBlocks = true;

    for(BasicBlock* exitBlock : *exitBlocks) {
        if(!dt->dominates(i->getParent(), exitBlock)) {
            dominatesExitBlocks = false;
            break;
        }
    }
    return !i->mayHaveSideEffects() || dominatesExitBlocks;
}

char LICMPass::ID = 0;
RegisterPass<LICMPass> X("coco-licm", "Loop-Invariant Code Motion optimization");
