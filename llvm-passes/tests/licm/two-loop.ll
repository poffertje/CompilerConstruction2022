define i32 @main() {
entry:
  ; CHECK: br label %entry.while.cond
  br label %entry.while.cond

entry.while.cond:                                 ; preds = %entry.while.body, %entry
  %i.0 = phi i32 [ 1, %entry ], [ %.7, %entry.while.body ]
  %.6 = icmp slt i32 %i.0, 10
  br i1 %.6, label %entry.while.body, label %entry.endwhile

entry.while.body:                                 ; preds = %entry.while.cond
  ; CHECK: %.7 = add i32 %i.0, 1
  %.7 = add i32 %i.0, 1
  ; CHECK-NOT: %x = add i32 1, 1
  %x = add i32 1, 1
  ; CHECK-NOT: %y = add i32 1, 1
  %y = add i32 1, 1
  br label %entry.while.cond

entry.endwhile:                                   ; preds = %entry.while.cond
  ; CHECK: %z = add i32 1, 1
  br label %entry.endwhile.while.cond

entry.endwhile.while.cond:                        ; preds = %entry.endwhile.while.body, %entry.endwhile
  %i.3.0 = phi i32 [ 1, %entry.endwhile ], [ %.15, %entry.endwhile.while.body ]
  %.14 = icmp slt i32 %i.3.0, 20
  br i1 %.14, label %entry.endwhile.while.body, label %entry.endwhile.endwhile

entry.endwhile.while.body:                        ; preds = %entry.endwhile.while.cond
  ; CHECK: %.15 = add i32 %i.3.0, 1
  %.15 = add i32 %i.3.0, 1
  ; CHECK-NOT: %z = add i32 1, 1
  %z = add i32 1, 1
  br label %entry.endwhile.while.cond

entry.endwhile.endwhile:                          ; preds = %entry.endwhile.while.cond
  ret i32 0
}
