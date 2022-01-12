; CHECK: @f
define void @f(i1 %cond1, i1 %cond2, i32 %s1, i32 %s2, i32 %off) {
lbl.entry:
; CHECK: %a = alloca i32, i32 %s1
; CHECK: %b = alloca i32, i32 %s2
  %a = alloca i32, i32 %s1
  %b = alloca i32, i32 %s2
  br label %lbl.loop

; CHECK: lbl.loop:
lbl.loop:
; CHECK-DAG: %arr = phi i32* [ %a, %lbl.entry ], [ %b, %lbl.loop.if1 ], [ %arr, %lbl.loop.if2 ]
; CHECK-DAG: [[PHI:%.*]] = phi i32 [ %s1, %lbl.entry ], [ %s2, %lbl.loop.if1 ], [ [[PHI]], %lbl.loop.if2 ]
  %arr = phi i32* [ %a, %lbl.entry ], [ %b, %lbl.loop.if1 ], [ %arr, %lbl.loop.if2 ]
  br i1 %cond1, label %lbl.loop.if1, label %lbl.loop.if2

; CHECK: lbl.loop.if1:
lbl.loop.if1:
  br i1 %cond2, label %lbl.loop, label %lbl.exit

; CHECK: lbl.loop.if2:
lbl.loop.if2:
  br i1 %cond2, label %lbl.loop, label %lbl.exit

; CHECK: lbl.exit:
lbl.exit:
; CHECK: call void @__coco_check_bounds({{.*}}i32 %off, i32 [[PHI]]{{.*}})
; CHECK: %gep = getelementptr i32, i32* %arr, i32 %off
  %gep = getelementptr i32, i32* %arr, i32 %off
  store i32 1, i32* %gep
  ret void
}


