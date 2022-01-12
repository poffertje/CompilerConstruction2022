define i32 @main() #0 {
  ; CHECK: %1 = alloca i32, align 4
  %1 = alloca i32, align 4
  ; CHECK: load i32, i32* %1, align 4
  %2 = load i32, i32* %1, align 4
  ; CHECK-NOT: %3 = alloca i32, align 4
  %3 = alloca i32, align 4
  call i32* @myfun()
  ret i32 %2
}

define i32* @myfun() #0 {
  ; CHECK: %1 = alloca i32, align 4
  %1 = alloca i32, align 4
  ; CHECK-NOT: load i32
  %2 = load i32, i32* %1, align 4
  %3 = alloca i32, align 4
  ; CHECK: store i32 42
  store i32 42, i32* %3
  ret i32* %3
}
