define i32 @main() #0 {
  ; CHECK: %1 = alloca i32, align 4
  %1 = alloca i32, align 4
  ; CHECK: load i32, i32* %1, align 4
  %2 = load i32, i32* %1, align 4
  ; CHECK-NOT: %3 = alloca i32, align 4
  %3 = alloca i32, align 4
  ret i32 %2
}
