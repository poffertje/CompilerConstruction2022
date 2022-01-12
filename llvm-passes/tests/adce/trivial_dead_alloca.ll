; RUN opt  < %s -load ../../llvm-passes/obj/libllvm-passes.so -coco-adce  -S | FileCheck %s

; CHECK: @main
define i32 @main() #0 {
; CHECK-NOT: %1 = alloca i32, align 4
  %1 = alloca i32, align 4
  ret i32 0
}
