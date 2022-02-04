; CHECK: @f
define void @f(i64 %o) {
; CHECK: %a = alloca i32, i32 16
  %a = alloca i32, i32 16
; CHECK-NOT: call void @__coco_check_bounds
; CHECK: %a.idx = getelementptr i32, i32* %a, i64 %o
  %a.idx = getelementptr i32, i32* %a, i64 %o
  store i32 1337, i32* %a.idx
  ret void
}
