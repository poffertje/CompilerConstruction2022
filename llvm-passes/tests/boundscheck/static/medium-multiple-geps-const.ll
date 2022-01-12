; CHECK: @f
define void @f() {
; CHECK: %a = alloca i32, i32 10
  %a = alloca i32, i32 10
; CHECK: call void @__coco_check_bounds({{.*}}i32 1, i32 10{{.*}})
; CHECK: %a.off1 = getelementptr i32, i32* %a, i32 1
  %a.off1 = getelementptr i32, i32* %a, i32 1
; CHECK: call void @__coco_check_bounds({{.*}}i32 5, i32 10{{.*}})
; CHECK: %a.off2 = getelementptr i32, i32* %a.off1, i32 4
  %a.off2 = getelementptr i32, i32* %a.off1, i32 4
  store i32 1337, i32* %a.off2
  ret void
}
