define i32 @main() {
entry:
  ; CHECK: %a = bitcast i32 255 to i32
  ; CHECK: br label %entry.while.cond
  br label %entry.while.cond

entry.while.cond:                                 ; preds = %entry.while.body, %entry
  %i.0 = phi i32 [ 1, %entry ], [ %.7, %entry.while.body ]
  %.6 = icmp slt i32 %i.0, 10
  br i1 %.6, label %entry.while.body, label %entry.endwhile

entry.while.body:                                 ; preds = %entry.while.cond
  ; CHECK: %.7 = add i32 %i.0, 1
  %.7 = add i32 %i.0, 1
  ; CHECK-NOT: %a = bitcast i32 255 to i32
  %a = bitcast i32 255 to i32
  %x = add i32 1, %a
  br label %entry.while.cond

entry.endwhile:                                   ; preds = %entry.while.cond
  ret i32 0
}
