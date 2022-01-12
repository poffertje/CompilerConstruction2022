; CHECK: @f
define void @f(i32 %o) {
; CHECK: %a = alloca i32, i32 16
  %a = alloca i32, i32 16
; CHECK: call void @__coco_check_bounds({{.*}}i32 %o, i32 16{{.*}})
; CHECK: %a.idx = getelementptr i32, i32* %a, i32 %o
  %a.idx = getelementptr i32, i32* %a, i32 %o
  store i32 1337, i32* %a.idx
  ret void
}
