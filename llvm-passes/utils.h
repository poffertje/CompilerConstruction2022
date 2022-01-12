#ifndef UTILS_H
#define UTILS_H

#include <string>
#include <cassert>

#include <llvm/Pass.h>
#include <llvm/IR/Module.h>
#include <llvm/IR/Function.h>
#include <llvm/IR/Instruction.h>
#include <llvm/IR/Instructions.h>
#include <llvm/IR/IntrinsicInst.h>
#include <llvm/IR/Intrinsics.h>
#include <llvm/IR/InstIterator.h>
#include <llvm/IR/Constant.h>
#include <llvm/IR/Constants.h>
#include <llvm/IR/Dominators.h>
#include <llvm/IR/IRBuilder.h>
#include <llvm/ADT/Statistic.h>
#include <llvm/ADT/DepthFirstIterator.h>
#include <llvm/Analysis/LoopInfo.h>
#include <llvm/Analysis/LoopPass.h>
#include <llvm/Transforms/Utils/Local.h>
#include <llvm/Transforms/Utils/ValueMapper.h>
#include <llvm/Transforms/Utils/Cloning.h>
#include <llvm/Transforms/Utils/BasicBlockUtils.h>
#include <llvm/Transforms/Utils/LoopUtils.h>
#include <llvm/Support/raw_ostream.h>

// Logging functions for errors and debug information
#ifdef DEBUG_TYPE
# define LOG_LINE(line) (errs() << "[" DEBUG_TYPE "] " << line << '\n')
#else
# define LOG_LINE(line) (errs() << line << '\n')
#endif

#define DEBUG_LINE(line) LLVM_DEBUG(LOG_LINE(line))

#define ERROR(msg) \
    do { \
        LOG_LINE(msg); \
        exit(1); \
    } while (0)

using namespace llvm;

/*
 * Returns whether a given function should be instrumented by your passes. This
 * is primarily used to exclude helper function from being instrumented.
 * For instance, when using a helper function to perform bounds checks, you do
 * not want that function itself to receive bounds checks.
 */
bool shouldInstrument(Function *F);

/*
 * Adds new parameters (of given types) to a function. Since you cannot change
 * function signatures in LLVM, this function instead creates a *new* function,
 * a clone of the old one, with the updated signature. The newly created
 * function is returned, and all added parameters (the argument variables) are
 * returned in the provided NewArgs list.
 *
 * The newly created parameters (in NewArgs) will not have names. You can
 * manually set these using setName.
 */
Function *addParamsToFunction(Function *F, ArrayRef<Type*> NewParamTypes,
        SmallVectorImpl<Argument*> &NewArgs);

#endif /* !UTILS_H */
