define i32 @main() {
entry:
  %a = alloca i32, i32 100
  %.2 = bitcast i32* %a to i8*
  %nbytes = mul i32 100, 4
  call void @llvm.memset.p0i8.i32(i8* %.2, i8 0, i32 %nbytes, i32 4, i1 false)
  ; CHECK: br label %entry.while.cond
  br label %entry.while.cond

entry.while.cond:                                 ; preds = %entry.while.body, %entry
  %i.0 = phi i32 [ 0, %entry ], [ %.9, %entry.while.body ]
  %.7 = icmp slt i32 %i.0, 10
  br i1 %.7, label %entry.while.body, label %entry.endwhile

entry.while.body:                                 ; preds = %entry.while.cond
  ; CHECK-NOT: %a.idx = getelementptr i32, i32* %a, i32 1
  %a.idx = getelementptr i32, i32* %a, i32 1
  ; CHECK: store i32 5, i32* %a.idx
  store i32 5, i32* %a.idx
  %.9 = add i32 %i.0, 1
  br label %entry.while.cond

entry.endwhile:                                   ; preds = %entry.while.cond
  ret i32 1
}

; Function Attrs: argmemonly nounwind
declare void @llvm.memset.p0i8.i32(i8* nocapture writeonly, i8, i32, i32, i1) #0
