define i32 @main() {
entry:
  br label %entry.while.cond

entry.while.cond:                                 ; preds = %entry.while.body, %entry
  %i.0 = phi i32 [ 1, %entry ], [ %.7, %entry.while.body ]
  %.6 = icmp slt i32 %i.0, 10
  %a = alloca i32, i32 1
  store i32 4, i32* %a
  %f = load volatile i32, i32* %a
  br i1 %.6, label %entry.while.body, label %entry.endwhile

entry.while.body:                                 ; preds = %entry.while.cond
  %b = alloca i32, i32 1
  store i32 7, i32* %b
  %c = load i32, i32* %b
  %.7 = lshr i32 %i.0, %c
  ; CHECK: %.8 = lshr i32 %i.0, %f
  %.8 = lshr i32 %i.0, %f
  ; CHECK: %x = lshr i32 %.7, %f
  %x = lshr i32 %.7, %f
  br label %entry.while.cond

entry.endwhile:                                   ; preds = %entry.while.cond
  ret i32 0
}
