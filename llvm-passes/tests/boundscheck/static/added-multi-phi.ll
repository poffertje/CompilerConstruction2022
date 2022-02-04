; CHECK: @f
define void @f(i1 %cond, i1 %cond2, i32 %s1, i32 %s2, i32 %off) {
; CHECK: %a = alloca i32, i32 %s1
; CHECK: %b = alloca i32, i32 %s2
  %a = alloca i32, i32 %s1
  %b = alloca i32, i32 %s2
  br i1 %cond, label %lbl.if, label %lbl.else

lbl.if:
  br i1 %cond2, label %lbl.phi1, label %lbl.phi2
lbl.else:
  br i1 %cond2, label %lbl.phi1, label %lbl.phi2

; CHECK: lbl.phi1
lbl.phi1:
; CHECK-DAG: %arr1 = phi i32* [ %a, %lbl.if ], [ %b, %lbl.else ]
; CHECK-DAG: [[PHI1:%.*]] = phi i32 [ %s1, %lbl.if ], [ %s2, %lbl.else ]
  %arr1 = phi i32* [ %a, %lbl.if ], [ %b, %lbl.else ]
  br label %lbl.phi3

; CHECK: lbl.phi2
lbl.phi2:
; CHECK-DAG: %arr2 = phi i32* [ %b, %lbl.if ], [ %a, %lbl.else ]
; CHECK-DAG: [[PHI2:%.*]] = phi i32 [ %s2, %lbl.if ], [ %s1, %lbl.else ]
  %arr2 = phi i32* [ %b, %lbl.if ], [ %a, %lbl.else ]
  br label %lbl.phi3

; CHECK: lbl.phi3
lbl.phi3:
; CHECK-DAG: %arr3 = phi i32* [ %arr1, %lbl.phi1 ], [ %arr2, %lbl.phi2 ]
; CHECK-DAG: [[PHI3:%.*]] = phi i32 [ [[PHI1]], %lbl.phi1 ], [ [[PHI2]], %lbl.phi2 ]
  %arr3 = phi i32* [ %arr1, %lbl.phi1 ], [ %arr2, %lbl.phi2 ]

; CHECK: call void @__coco_check_bounds({{.*}}i32 %off, i32 [[PHI3]]{{.*}})
; CHECK: %gep = getelementptr i32, i32* %arr3, i32 %off
  %gep = getelementptr i32, i32* %arr3, i32 %off
  store i32 1, i32* %gep
  ret void
}


