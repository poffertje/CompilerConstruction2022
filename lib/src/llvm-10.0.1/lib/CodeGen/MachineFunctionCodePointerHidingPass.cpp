//===-- MachineFunctionPrinterPass.cpp ------------------------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//
//
// MachineFunctionCodePointerHidingPass implementation.
//
//===----------------------------------------------------------------------===//

#include "llvm/CodeGen/MachineFunction.h"
#include "llvm/CodeGen/MachineFunctionPass.h"
#include "llvm/CodeGen/Passes.h"
#include "llvm/CodeGen/SlotIndexes.h"
#include "llvm/CodeGen/TargetSubtargetInfo.h"
#include "llvm/CodeGen/TargetInstrInfo.h"
#include "llvm/IR/IRPrintingPasses.h"
#include "llvm/IR/Module.h"
#include "llvm/Support/Debug.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Support/RandomNumberGenerator.h"
#include "llvm/Target/TargetMachine.h"
#include "llvm/InitializePasses.h"

#define DEBUG_TYPE "code_pointer_hiding"

using namespace llvm;

namespace {
/// MachineFunctionCodePointerHidingPass - This is a pass that adds NOP sleds to
/// specific parts of the generated machine code.
/// In particular:
///   - Before the first/last instruction in a function
///   - Before each call site
///   - After each call site 
///
struct MachineFunctionCodePointerHidingPass : public MachineFunctionPass {
  static char ID;

  MachineFunctionCodePointerHidingPass() : MachineFunctionPass(ID), NOPSledMaxSize(0) {}

  MachineFunctionCodePointerHidingPass(unsigned NOPSledMaxSize)
    : MachineFunctionPass(ID), NOPSledMaxSize(NOPSledMaxSize) { }

  StringRef getPassName() const override { return "MachineFunction Code Pointer Hiding"; }

  void getAnalysisUsage(AnalysisUsage &AU) const override {
    AU.setPreservesAll();
    AU.addUsedIfAvailable<SlotIndexes>();
    MachineFunctionPass::getAnalysisUsage(AU);
  }

  bool runOnMachineFunction(MachineFunction &MF) override;

private:
  unsigned NOPSledMaxSize;
  unsigned NOPOpcode;
  std::unique_ptr<RandomNumberGenerator> rng;

  MachineInstr* createInstrNOP(MachineFunction& MF);
  unsigned getNOPOpcodeForMachine(TargetMachine& machine);
  MachineBasicBlock::instr_iterator insertRandomNOPs(MachineBasicBlock &MBB, MachineBasicBlock::instr_iterator pos, bool insertAfter = false);
  size_t rand();
};

bool MachineFunctionCodePointerHidingPass::runOnMachineFunction(MachineFunction &MF) {
  LLVM_DEBUG(dbgs() << "##### CODE POINTER HIDING PASS #####\n");

  // Init pass
  rng = MF.getFunction().getParent()->createRNG(this);

  MCInst MI;
  MF.getSubtarget().getInstrInfo()->getNoop(MI);
  NOPOpcode = MI.getOpcode();

  // Insert NOPs before the first instruction
  insertRandomNOPs(MF.front(), MF.front().instr_begin());

  // Insert NOPs before and after every call site
  SmallDenseMap<MachineBasicBlock*, SmallVector<MachineBasicBlock::instr_iterator, 16>, 16> insertionPoints;

  for(MachineBasicBlock &MBB : MF) {
    for(MachineBasicBlock::instr_iterator iter = MBB.instr_begin(); iter != MBB.instr_end(); iter++) {
      MachineInstr &instr = *iter;
      if(instr.isCall()) {
        if(insertionPoints.count(&MBB) == 0) {
          insertionPoints.insert({&MBB, {iter}});
        } else {
          insertionPoints[&MBB].push_back(iter);
        }
      }
    }
  }

  for(auto mbb_iter = insertionPoints.begin(); mbb_iter != insertionPoints.end(); mbb_iter++) {
    auto pair = *mbb_iter;
    MachineBasicBlock *MBB = pair.first;
    SmallVector<MachineBasicBlock::instr_iterator, 16> &vec = pair.second;
    for(MachineBasicBlock::instr_iterator &iter : vec) {
      insertRandomNOPs(*MBB, iter);
      insertRandomNOPs(*MBB, iter, true);
    }
  }

  // Insert NOPs before the last instruction
  insertRandomNOPs(MF.back(), --MF.back().instr_end());

  return true;
}

MachineBasicBlock::instr_iterator MachineFunctionCodePointerHidingPass::insertRandomNOPs(MachineBasicBlock &MBB, MachineBasicBlock::instr_iterator pos, bool insertAfter) {
  size_t sledSize = rand();
  LLVM_DEBUG(dbgs() << "sled size: " << sledSize << "\n");
  LLVM_DEBUG(dbgs() << "pos: " << *pos << "\n");

  for(size_t i = 0; i < sledSize; i++) {
    MachineInstr* inst = createInstrNOP(*MBB.getParent());
    inst->setDebugLoc((*pos).getDebugLoc());
    if(insertAfter) {
      MBB.insertAfter(pos, inst);
    } else {
      pos = MBB.insert(pos, inst);
    }
    pos++;
  }

  LLVM_DEBUG(dbgs() << "Updated block: " << MBB << "\n");
  return pos;
}

// Get a random number bettween 0 and NOPSledMaxSize included: [0, NOPSledMaxSize]
size_t MachineFunctionCodePointerHidingPass::rand() {
  return ((*rng)() % (NOPSledMaxSize + 1));
}


MachineInstr* MachineFunctionCodePointerHidingPass::createInstrNOP(MachineFunction& MF) {
  // DebugLoc is set to first instruction of the function,
  // this has to be updated later when positional information is available
  return MF.CreateMachineInstr(MF.getTarget().getMCInstrInfo()->get(NOPOpcode), MF.front().front().getDebugLoc());
}

char MachineFunctionCodePointerHidingPass::ID = 0;
}

char &llvm::MachineFunctionCodePointerHidingPassID = MachineFunctionCodePointerHidingPass::ID;
INITIALIZE_PASS(MachineFunctionCodePointerHidingPass, "machineinstr-code-pointer-hiding",
                "Machine Function Code Pointer Hiding", false, false)

namespace llvm {
/// Returns a newly-created MachineFunction Code Pointer Hiding pass.
///
MachineFunctionPass *createMachineFunctionCodePointerHidingPass(unsigned NOPSledMaxSize){
  return new MachineFunctionCodePointerHidingPass(NOPSledMaxSize);
}

}
