; CHECK: @f
define void @f(i1 %cond, i32 %s1, i32 %s2, i32 %off) {
; CHECK: %a = alloca i32, i32 %s1
; CHECK: %b = alloca i32, i32 %s2
  %a = alloca i32, i32 %s1
  %b = alloca i32, i32 %s2
  br i1 %cond, label %lbl.if, label %lbl.else

lbl.if:
  br label %lbl.exit
lbl.else:
  br label %lbl.exit

; CHECK: lbl.exit
lbl.exit:
; CHECK-DAG: %arr = phi i32* [ %a, %lbl.if ], [ %b, %lbl.else ]
; CHECK-DAG: [[PHI:%.*]] = phi i32 [ %s1, %lbl.if ], [ %s2, %lbl.else ]
  %arr = phi i32* [ %a, %lbl.if ], [ %b, %lbl.else ]
; CHECK: call void @__coco_check_bounds({{.*}}i32 %off, i32 [[PHI]]{{.*}})
; CHECK: %gep = getelementptr i32, i32* %arr, i32 %off
  %gep = getelementptr i32, i32* %arr, i32 %off
  store i32 1, i32* %gep
  ret void
}


