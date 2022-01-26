/*
 * Dummy (and minimal) function pass to serve as a starting point for your
 * Assignment 2 passes. It simply visits every function and prints every call
 * instruction it finds.
 */

#define DEBUG_TYPE "ADCEPass"
#include "utils.h"

namespace {
    class ADCEPass : public FunctionPass {
    public:
        static char ID;
        ADCEPass() : FunctionPass(ID) {}
        virtual bool runOnFunction(Function &F) override;
    private:
        bool isTriviallyLive(Instruction& i);
    };
}

bool ADCEPass::runOnFunction(Function &f) {
    LOG_LINE("Visiting function " << f.getName());
    bool modified = false;
    DenseSet<Instruction*> liveSet;
    df_iterator_default_set<BasicBlock*> reachableSet;
    SmallVector<Instruction*, 32> workList;
    SmallVector<Instruction*, 32> toErase;

    for (BasicBlock* bb : depth_first_ext(&f, reachableSet)) {
        for (Instruction &ii : *bb) {
            Instruction *i = &ii;
            if (isTriviallyLive(*i)) {
                LOG_LINE("Trivially live: " << *i);
                liveSet.insert(i);
                workList.push_back(i);
            } else if(i->use_empty()) {
                LOG_LINE("Erasing: " << *i);
                toErase.push_back(i);
            }
        }
    }

    for(Instruction* i : toErase) {
        i->eraseFromParent();
        modified = true;
    }
    toErase.clear();
    
    while(!workList.empty()) {
        Instruction* i = workList.pop_back_val();
        LOG_LINE("working on: " << *i);
        if (reachableSet.count(i->getParent()) == 1) {
            LOG_LINE("Reachable");
            for (Use &u : i->operands()) {
                Value *v = u.get();
                LOG_LINE("Operand: " << *v);
                if(Instruction* op = dyn_cast<Instruction>(v)) {
                    LOG_LINE("Is instruction");
                    if(liveSet.count(op) == 0) {
                        liveSet.insert(op);
                        workList.push_back(op);
                    }
                }
            }
        } else {
            LOG_LINE("Unreachable");
        }

    }

    for (BasicBlock &bb : f) {
        if (reachableSet.count(&bb) == 1) {
            for(Instruction &i : bb) {
                if(liveSet.count(&i) == 0) {
                    i.dropAllReferences();
                    modified = true;
                }
            }
        }
    }

    for (BasicBlock &bb : f) {
        if (reachableSet.count(&bb) == 1) {
            for(Instruction &i : bb) {
                if(liveSet.count(&i) == 0) {
                    toErase.push_back(&i);
                }
            }
        }
    }

    for(Instruction* i : toErase) {
        i->eraseFromParent();
        modified = true;
    }

    return modified;  // We did not alter the IR
}

bool ADCEPass::isTriviallyLive(Instruction& i) {
    bool volatileLoad = false;
    LOG_LINE("Checking: " << i);
    if (LoadInst* li = dyn_cast<LoadInst>(&i)) {
        LOG_LINE(*li);
        volatileLoad = li->isVolatile();
    }
    return i.mayHaveSideEffects() || i.isTerminator()
        || isa<StoreInst>(i) || isa<CallInst>(i) || volatileLoad;
}

// Register the pass with LLVM so we can invoke it with opt. The first argument
// to RegisterPass is the commandline switch to run this pass (e.g., opt
// -coco-dummypass, the second argument is a description shown in the help text
// about this pass.
char ADCEPass::ID = 0;
static RegisterPass<ADCEPass> X("coco-adce", "Aggressive dead code elimination pass");
