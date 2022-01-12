define i32 @main() {
entry:
  ; CHECK: %x = sub i32 1, 1
  ; CHECK: br label %entry.while.cond
  br label %entry.while.cond

entry.while.cond:                                 ; preds = %entry.while.body, %entry
  %i.0 = phi i32 [ 1, %entry ], [ %.7, %entry.while.body ]
  %.6 = icmp slt i32 %i.0, 10
  br i1 %.6, label %entry.while.body, label %entry.endwhile

entry.while.body:                                 ; preds = %entry.while.cond
  ; CHECK: %.7 = sub i32 %i.0, 1
  %.7 = sub i32 %i.0, 1
  ; CHECK-NOT: %x = sub i32 1, 1
  %x = sub i32 1, 1
  br label %entry.while.cond

entry.endwhile:                                   ; preds = %entry.while.cond
  ret i32 0
}
