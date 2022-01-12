@.str = private unnamed_addr constant [7 x i8] c"a: %d\0A\00", align 1

define i32 @main() #0 {
  ; CHECK: %1 = alloca i32, align 4
  %1 = alloca i32, align 4
  ; CHECK: %2 = alloca i32, align 4
  %2 = alloca i32, align 4
  ; CHECK: %3 = alloca i32, align 4
  %3 = alloca i32, align 4
  ; CHECK-NOT: %4 = alloca i32, align 4
  %4 = alloca i32, align 4
  ; CHECK-NOT: %5 = alloca i32, align 4
  %5 = alloca i32, align 4
  store i32 0, i32* %1, align 4
  store i32 42, i32* %2, align 4
  store i32 1, i32* %3, align 4
  %6 = load i32, i32* %2, align 4
  %7 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([7 x i8], [7 x i8]* @.str, i32 0, i32 0), i32 %6)
  ret i32 0
}

declare i32 @printf(i8*, ...) #1
