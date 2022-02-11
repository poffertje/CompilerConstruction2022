; ModuleID = '<string>'
source_filename = "<string>"
target triple = "x86_64-unknown-linux-gnu"

@.str.0 = unnamed_addr constant [14 x i8] c"Hello, World!\00"

declare i32 @random()

declare void @srandom(i32)

declare i32 @printf(i8*, ...)

declare i32 @puts(i8*)

declare i32 @atoi(i8*)

declare void @exit(i32)

define i32 @main(i32 %param.argc, i8** %argv) {
entry:
  %argc = alloca i32
  store i32 %param.argc, i32* %argc
  %.str.0 = getelementptr inbounds [14 x i8], [14 x i8]* @.str.0, i32 0, i32 0
  %.5 = call i32 @puts(i8* %.str.0)
  ret i32 0
}
