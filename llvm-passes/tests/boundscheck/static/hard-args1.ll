; CHECK: @g{{.*}}(i32* %a, i32 [[SARG:%.*]])
define void @g(i32* %a) {
; CHECK: call void @__coco_check_bounds({{.*}}i32 100, i32 [[SARG]]{{.*}})
; CHECK: %a.idx = getelementptr i32, i32* %a, i32 100
  %a.idx = getelementptr i32, i32* %a, i32 100
  store i32 1337, i32* %a.idx
  ret void
}
; CHECK: @f
define void @f(i32 %s) {
; CHECK: %arr = alloca i32, i32 %s
  %arr = alloca i32, i32 %s
; CHECK: call void @g{{.*}}(i32* %arr, i32 %s)
  call void @g(i32* %arr)
  ret void
}
