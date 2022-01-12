@.str = unnamed_addr constant [4 x i8] c"foo\00"

; CHECK: @f
define void @f(i32 %o) {
; CHECK-NOT: call
; CHECK:  %.str.1 = getelementptr [4 x i8], [4 x i8]* @.str, i32 0, i32 0
  %.str.1 = getelementptr [4 x i8], [4 x i8]* @.str, i32 0, i32 0

; CHECK: call void @__coco_check_bounds({{.*}}i32 1, i32 4{{.*}})
; CHECK: %.str.idx = getelementptr i8, i8* %.str.1, i32 1
  %.str.idx = getelementptr i8, i8* %.str.1, i32 1
  store i8 1, i8* %.str.idx

; CHECK: call void @__coco_check_bounds({{.*}}i32 9, i32 4{{.*}})
; CHECK: %.str.idx2 = getelementptr i8, i8* %.str.1, i32 9
  %.str.idx2 = getelementptr i8, i8* %.str.1, i32 9
  store i8 1, i8* %.str.idx2
  ret void
}
