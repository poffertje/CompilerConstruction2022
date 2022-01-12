define i32 @main() {
entry:
  %t = add i32 2, 2
  br label %entry.while.cond

entry.while.cond:                                 ; preds = %entry.while.body, %entry
  %i.0 = phi i32 [ 1, %entry ], [ %.7, %entry.while.body ]
  %.6 = icmp slt i32 %i.0, 10
  br i1 %.6, label %entry.while.body, label %entry.endwhile

entry.while.body:                                 ; preds = %entry.while.cond
  %a = alloca i32, i32 1
  ; CHECK: %.7 = add i32 %i.0, 1
  %.7 = add i32 %i.0, 1
  %x = add i32 2, %t
  %y = add i32 2, %x
  %z = shl i32 2, %y
  %q = add i32 2, %z
  ; CHECK: %r = add i32 2, 514
  %r = add i32 2, %q
  ; CHECK: store volatile i32 516, i32* %a
  store volatile i32 %r, i32* %a
  br label %entry.while.cond

entry.endwhile:                                   ; preds = %entry.while.cond
  ret i32 0
}
