define i32 @main() {
entry:
  %nbytes = mul i32 100, 4
  br label %entry.while.cond

entry.while.cond:                                 ; preds = %entry.while.body, %entry
  %i.0 = phi i32 [ 0, %entry ], [ %.9, %entry.while.body ]
  %.7 = icmp slt i32 %i.0, 10
  br i1 %.7, label %entry.while.body, label %entry.endwhile

  ; CHECK: entry.while.body:
entry.while.body:                                 ; preds = %entry.while.cond
  %z = alloca i32, i32 1
  ; CHECK-NOT: %x = select i1 true, i32 17, i32 42
  %x = select i1 true, i32 17, i32 42
  store i32 %x, i32* %z
  %.9 = add i32 %i.0, 1
  br label %entry.while.cond

entry.endwhile:                                   ; preds = %entry.while.cond
  ret i32 1
}

; Function Attrs: argmemonly nounwind
declare void @llvm.memset.p0i8.i32(i8* nocapture writeonly, i8, i32, i32, i1) #0
