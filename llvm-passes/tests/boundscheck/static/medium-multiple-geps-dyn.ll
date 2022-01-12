; CHECK: @f
define void @f(i32 %o1, i32 %o2) {
; CHECK: %a = alloca i32, i32 10
  %a = alloca i32, i32 10
; CHECK: call void @__coco_check_bounds({{.*}}i32 %o1, i32 10{{.*}})
; CHECK: %a.off1 = getelementptr i32, i32* %a, i32 %o1
  %a.off1 = getelementptr i32, i32* %a, i32 %o1
; CHECK: [[ADD:%.*]] = add i32 %o{{[12]}}, %o{{[12]}}
; CHECK: call void @__coco_check_bounds({{.*}}i32 [[ADD]], i32 10{{.*}})
; CHECK: %a.off2 = getelementptr i32, i32* %a.off1, i32 %o2
  %a.off2 = getelementptr i32, i32* %a.off1, i32 %o2
  store i32 1337, i32* %a.off2
  ret void
}
