define i32 @main() {
entry:
  br label %entry.while.cond

entry.while.cond:                                 ; preds = %entry.while.body, %entry
  %i.0 = phi i32 [ 1, %entry ], [ %.7, %entry.while.body ]
  %.6 = icmp slt i32 %i.0, 10
  br i1 %.6, label %entry.while.body, label %entry.endwhile

entry.while.body:                                 ; preds = %entry.while.cond
  %a = alloca double, i32 1
  %b = alloca double, i32 1
  store volatile double 42.0, double* %b
  %l = load volatile double, double* %b
  ; CHECK: %.7 = add i32 %i.0, 1
  %.7 = add i32 %i.0, 1

  ; checking x * 1

  %z = fmul double %l, 1.0
  %w = fmul double 1.0, %l
  ; CHECK: store volatile double %l, double* %a
  store volatile double %z, double* %a
  ; CHECK: store volatile double %l, double* %a
  store volatile double %w, double* %a
  
  br label %entry.while.cond

entry.endwhile:                                   ; preds = %entry.while.cond
  ret i32 0
}
