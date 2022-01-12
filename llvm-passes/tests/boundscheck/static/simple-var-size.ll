; CHECK: @f
define void @f(i32 %s) {
; CHECK: %a = alloca i32, i32 %s
  %a = alloca i32, i32 %s
; CHECK: call void @__coco_check_bounds({{.*}}i32 100, i32 %s{{.*}})
; CHECK: %a.idx = getelementptr i32, i32* %a, i32 100
  %a.idx = getelementptr i32, i32* %a, i32 100
  store i32 1337, i32* %a.idx
  ret void
}
