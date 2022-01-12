define i32 @main() #0 {
  ; CHECK-NOT: %1 = alloca i32, align 4
  %1 = alloca i32, align 4
  ; CHECK-NOT: load i32, i32* %1, align 4
  %2 = load i32, i32* %1, align 4
  ret i32 0
}
