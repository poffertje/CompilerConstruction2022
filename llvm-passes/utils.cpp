#include "utils.h"

bool shouldInstrument(Function *F) {
    if (F->isDeclaration())
        return false;
    if (F->getName().startswith("__coco"))
        return false;

    return true;
}

Function *addParamsToFunction(Function *F, ArrayRef<Type*> NewParamTypes,
        SmallVectorImpl<Argument*> &NewArgs) {
    if (NewParamTypes.size() == 0)
        ERROR("addParamsToFunction called without new params to add");
    if (NewArgs.size() != 0)
        ERROR("addParamsToFunction called with non-empty NewArgs (should only be used as return value).");

    FunctionType *OldFuncTy = F->getFunctionType();

    SmallVector<Type*, 8> NewArgTys;
    for (Type *ArgTy : OldFuncTy->params())
        NewArgTys.push_back(ArgTy);
    for (Type *ArgTy : NewParamTypes)
        NewArgTys.push_back(ArgTy);

    // Create the new function type and new (empty) function
    FunctionType *NewFuncTy = FunctionType::get(OldFuncTy->getReturnType(),
            NewArgTys, F->isVarArg());
    Function *NewFunc = Function::Create(NewFuncTy, F->getLinkage(), F->getName() + "_clone");
    F->getParent()->getFunctionList().insert(F->getIterator(), NewFunc); // Add to module

    // Map every argument of the old function to the new one
    ValueToValueMapTy ValueMap;
    Function::arg_iterator NI = NewFunc->arg_begin();
    for (Function::arg_iterator OI = F->arg_begin();
            OI != F->arg_end(); OI++, NI++) {
        ValueMap[OI] = NI;
        NI->setName(OI->getName());
    }

    // Return the new arguments
    for (; NI != NewFunc->arg_end(); NI++)
        NewArgs.push_back(NI);

    // Finally, clone all the code (basicblocks etc) of the old function into
    // the new one. We're not interested in the ReturnInsts.
    SmallVector<ReturnInst*, 8> ReturnInsts;
    CloneFunctionInto(NewFunc, F, ValueMap, true, ReturnInsts);

    return NewFunc;
}
