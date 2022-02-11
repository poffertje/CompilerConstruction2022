; ModuleID = '<string>'
source_filename = "<string>"
target triple = "x86_64-unknown-linux-gnu"

@.str.0 = unnamed_addr constant [2 x i8] c"Q\00"
@.str.1 = unnamed_addr constant [2 x i8] c".\00"
@.str.2 = unnamed_addr constant [2 x i8] c" \00"
@.str.3 = unnamed_addr constant [2 x i8] c"\0A\00"
@.str.4 = unnamed_addr constant [2 x i8] c"-\00"
@.str.5 = unnamed_addr constant [2 x i8] c"\0A\00"
@.str.6 = unnamed_addr constant [15 x i8] c"Usage: %s <N>\0A\00"

declare i32 @random()

declare void @srandom(i32)

declare i32 @printf(i8*, ...)

declare i32 @puts(i8*)

declare i32 @atoi(i8*)

declare void @exit(i32)

define void @printArray(i32 %param.N, i32* %a) {
entry:
  %N = alloca i32
  store i32 %param.N, i32* %N
  %i = alloca i32
  store i32 0, i32* %i
  br label %entry.whilecond

entry.whilecond:                                  ; preds = %entry.whilebody.endwhile, %entry
  %i.1 = load i32, i32* %i
  %N.1 = load i32, i32* %N
  %.7 = icmp slt i32 %i.1, %N.1
  br i1 %.7, label %entry.whilebody, label %entry.endwhile

entry.whilebody:                                  ; preds = %entry.whilecond
  %j = alloca i32
  store i32 0, i32* %j
  br label %entry.whilebody.whilecond

entry.whilebody.whilecond:                        ; preds = %entry.whilebody.whilebody.endif, %entry.whilebody
  %j.1 = load i32, i32* %j
  %N.2 = load i32, i32* %N
  %.11 = icmp slt i32 %j.1, %N.2
  br i1 %.11, label %entry.whilebody.whilebody, label %entry.whilebody.endwhile

entry.whilebody.whilebody:                        ; preds = %entry.whilebody.whilecond
  %j.2 = load i32, i32* %j
  %i.2 = load i32, i32* %i
  %a.ptr = getelementptr i32, i32* %a, i32 %i.2
  %a.idx = load i32, i32* %a.ptr
  %.13 = icmp eq i32 %j.2, %a.idx
  br i1 %.13, label %entry.whilebody.whilebody.if, label %entry.whilebody.whilebody.else

entry.whilebody.whilebody.if:                     ; preds = %entry.whilebody.whilebody
  %.str.0 = getelementptr inbounds [2 x i8], [2 x i8]* @.str.0, i32 0, i32 0
  %.15 = call i32 (i8*, ...) @printf(i8* %.str.0)
  br label %entry.whilebody.whilebody.endif

entry.whilebody.whilebody.else:                   ; preds = %entry.whilebody.whilebody
  %.str.1 = getelementptr inbounds [2 x i8], [2 x i8]* @.str.1, i32 0, i32 0
  %.17 = call i32 (i8*, ...) @printf(i8* %.str.1)
  br label %entry.whilebody.whilebody.endif

entry.whilebody.whilebody.endif:                  ; preds = %entry.whilebody.whilebody.else, %entry.whilebody.whilebody.if
  %.str.2 = getelementptr inbounds [2 x i8], [2 x i8]* @.str.2, i32 0, i32 0
  %.19 = call i32 (i8*, ...) @printf(i8* %.str.2)
  %j.3 = load i32, i32* %j
  %.20 = add i32 %j.3, 1
  store i32 %.20, i32* %j
  br label %entry.whilebody.whilecond

entry.whilebody.endwhile:                         ; preds = %entry.whilebody.whilecond
  %.str.3 = getelementptr inbounds [2 x i8], [2 x i8]* @.str.3, i32 0, i32 0
  %.23 = call i32 (i8*, ...) @printf(i8* %.str.3)
  %i.3 = load i32, i32* %i
  %.24 = add i32 %i.3, 1
  store i32 %.24, i32* %i
  br label %entry.whilecond

entry.endwhile:                                   ; preds = %entry.whilecond
  %i.4 = alloca i32
  store i32 0, i32* %i.4
  br label %entry.endwhile.whilecond

entry.endwhile.whilecond:                         ; preds = %entry.endwhile.whilebody, %entry.endwhile
  %i.5 = load i32, i32* %i.4
  %N.3 = load i32, i32* %N
  %.29 = mul i32 2, %N.3
  %.30 = icmp slt i32 %i.5, %.29
  br i1 %.30, label %entry.endwhile.whilebody, label %entry.endwhile.endwhile

entry.endwhile.whilebody:                         ; preds = %entry.endwhile.whilecond
  %.str.4 = getelementptr inbounds [2 x i8], [2 x i8]* @.str.4, i32 0, i32 0
  %.32 = call i32 (i8*, ...) @printf(i8* %.str.4)
  %i.6 = load i32, i32* %i.4
  %.33 = add i32 %i.6, 1
  store i32 %.33, i32* %i.4
  br label %entry.endwhile.whilecond

entry.endwhile.endwhile:                          ; preds = %entry.endwhile.whilecond
  %.str.5 = getelementptr inbounds [2 x i8], [2 x i8]* @.str.5, i32 0, i32 0
  %.36 = call i32 (i8*, ...) @printf(i8* %.str.5)
  ret void
}

define void @getPositions(i32 %param.N, i32* %a1, i32 %param.colno, i32 %param.val) {
entry:
  %N = alloca i32
  store i32 %param.N, i32* %N
  %colno = alloca i32
  store i32 %param.colno, i32* %colno
  %val = alloca i32
  store i32 %param.val, i32* %val
  %colno.1 = load i32, i32* %colno
  %a1.idx = getelementptr i32, i32* %a1, i32 %colno.1
  %val.1 = load i32, i32* %val
  store i32 %val.1, i32* %a1.idx
  %colno.2 = load i32, i32* %colno
  %N.1 = load i32, i32* %N
  %.10 = sub i32 %N.1, 1
  %.11 = icmp eq i32 %colno.2, %.10
  br i1 %.11, label %entry.if, label %entry.endif

entry.if:                                         ; preds = %entry
  %N.2 = load i32, i32* %N
  call void @printArray(i32 %N.2, i32* %a1)
  ret void

post_return:                                      ; No predecessors!
  br label %entry.endif

entry.endif:                                      ; preds = %post_return, %entry
  %ctr1 = alloca i32
  store i32 0, i32* %ctr1
  br label %entry.endif.whilecond

entry.endif.whilecond:                            ; preds = %entry.endif.whilebody.endwhile.endif, %entry.endif
  %ctr1.1 = load i32, i32* %ctr1
  %N.3 = load i32, i32* %N
  %.18 = icmp slt i32 %ctr1.1, %N.3
  br i1 %.18, label %entry.endif.whilebody, label %entry.endif.endwhile

entry.endif.whilebody:                            ; preds = %entry.endif.whilecond
  %keepgoing = alloca i32
  store i32 0, i32* %keepgoing
  %ctr2 = alloca i32
  store i32 0, i32* %ctr2
  br label %entry.endif.whilebody.whilecond

entry.endif.whilebody.whilecond:                  ; preds = %entry.endif.whilebody.whilebody.endif, %entry.endif.whilebody
  %ctr2.1 = load i32, i32* %ctr2
  %colno.3 = load i32, i32* %colno
  %.23 = add i32 %colno.3, 1
  %.24 = icmp slt i32 %ctr2.1, %.23
  br i1 %.24, label %entry.endif.whilebody.whilebody, label %entry.endif.whilebody.endwhile

entry.endif.whilebody.whilebody:                  ; preds = %entry.endif.whilebody.whilecond
  %ctr2.2 = load i32, i32* %ctr2
  %a1.ptr = getelementptr i32, i32* %a1, i32 %ctr2.2
  %a1.idx.1 = load i32, i32* %a1.ptr
  %ctr1.2 = load i32, i32* %ctr1
  %.26 = icmp eq i32 %a1.idx.1, %ctr1.2
  br i1 %.26, label %yes, label %no

yes:                                              ; preds = %entry.endif.whilebody.whilebody
  br label %endcond

no:                                               ; preds = %entry.endif.whilebody.whilebody
  %colno.4 = load i32, i32* %colno
  %.30 = add i32 %colno.4, 1
  %ctr2.3 = load i32, i32* %ctr2
  %.31 = sub i32 %.30, %ctr2.3
  %colno.5 = load i32, i32* %colno
  %.32 = add i32 %colno.5, 1
  %ctr2.4 = load i32, i32* %ctr2
  %.33 = sub i32 %.32, %ctr2.4
  %.34 = mul i32 %.31, %.33
  %ctr1.3 = load i32, i32* %ctr1
  %ctr2.5 = load i32, i32* %ctr2
  %a1.ptr.1 = getelementptr i32, i32* %a1, i32 %ctr2.5
  %a1.idx.2 = load i32, i32* %a1.ptr.1
  %.35 = sub i32 %ctr1.3, %a1.idx.2
  %ctr1.4 = load i32, i32* %ctr1
  %ctr2.6 = load i32, i32* %ctr2
  %a1.ptr.2 = getelementptr i32, i32* %a1, i32 %ctr2.6
  %a1.idx.3 = load i32, i32* %a1.ptr.2
  %.36 = sub i32 %ctr1.4, %a1.idx.3
  %.37 = mul i32 %.35, %.36
  %.38 = icmp eq i32 %.34, %.37
  br label %endcond

endcond:                                          ; preds = %no, %yes
  %.28 = phi i1 [ true, %yes ], [ %.38, %no ]
  br i1 %.28, label %entry.endif.whilebody.whilebody.if, label %entry.endif.whilebody.whilebody.endif

entry.endif.whilebody.whilebody.if:               ; preds = %endcond
  store i32 1, i32* %keepgoing
  br label %entry.endif.whilebody.whilebody.endif

entry.endif.whilebody.whilebody.endif:            ; preds = %entry.endif.whilebody.whilebody.if, %endcond
  %ctr2.7 = load i32, i32* %ctr2
  %.43 = add i32 %ctr2.7, 1
  store i32 %.43, i32* %ctr2
  br label %entry.endif.whilebody.whilecond

entry.endif.whilebody.endwhile:                   ; preds = %entry.endif.whilebody.whilecond
  %keepgoing.1 = load i32, i32* %keepgoing
  %.46 = icmp eq i32 %keepgoing.1, 0
  br i1 %.46, label %entry.endif.whilebody.endwhile.if, label %entry.endif.whilebody.endwhile.endif

entry.endif.whilebody.endwhile.if:                ; preds = %entry.endif.whilebody.endwhile
  %N.4 = load i32, i32* %N
  %colno.6 = load i32, i32* %colno
  %.48 = add i32 %colno.6, 1
  %ctr1.5 = load i32, i32* %ctr1
  call void @getPositions(i32 %N.4, i32* %a1, i32 %.48, i32 %ctr1.5)
  br label %entry.endif.whilebody.endwhile.endif

entry.endif.whilebody.endwhile.endif:             ; preds = %entry.endif.whilebody.endwhile.if, %entry.endif.whilebody.endwhile
  %ctr1.6 = load i32, i32* %ctr1
  %.51 = add i32 %ctr1.6, 1
  store i32 %.51, i32* %ctr1
  br label %entry.endif.whilecond

entry.endif.endwhile:                             ; preds = %entry.endif.whilecond
  ret void
}

define i32 @main(i32 %param.argc, i8** %argv) {
entry:
  %argc = alloca i32
  store i32 %param.argc, i32* %argc
  %argc.1 = load i32, i32* %argc
  %.5 = icmp ne i32 %argc.1, 2
  br i1 %.5, label %entry.if, label %entry.endif

entry.if:                                         ; preds = %entry
  %.str.6 = getelementptr inbounds [15 x i8], [15 x i8]* @.str.6, i32 0, i32 0
  %argv.ptr = getelementptr i8*, i8** %argv, i32 0
  %argv.idx = load i8*, i8** %argv.ptr
  %.7 = call i32 (i8*, ...) @printf(i8* %.str.6, i8* %argv.idx)
  ret i32 1

post_return:                                      ; No predecessors!
  br label %entry.endif

entry.endif:                                      ; preds = %post_return, %entry
  %N = alloca i32
  %argv.ptr.1 = getelementptr i8*, i8** %argv, i32 1
  %argv.idx.1 = load i8*, i8** %argv.ptr.1
  %.10 = call i32 @atoi(i8* %argv.idx.1)
  store i32 %.10, i32* %N
  %N.1 = load i32, i32* %N
  %a = alloca i32, i32 %N.1
  %.12 = bitcast i32* %a to i8*
  %nbytes = mul i32 %N.1, 4
  call void @llvm.memset.p0i8.i32(i8* %.12, i8 0, i32 %nbytes, i1 false)
  %i = alloca i32
  store i32 0, i32* %i
  br label %entry.endif.whilecond

entry.endif.whilecond:                            ; preds = %entry.endif.whilebody, %entry.endif
  %i.1 = load i32, i32* %i
  %N.2 = load i32, i32* %N
  %.16 = icmp slt i32 %i.1, %N.2
  br i1 %.16, label %entry.endif.whilebody, label %entry.endif.endwhile

entry.endif.whilebody:                            ; preds = %entry.endif.whilecond
  %N.3 = load i32, i32* %N
  %i.2 = load i32, i32* %i
  call void @getPositions(i32 %N.3, i32* %a, i32 0, i32 %i.2)
  %i.3 = load i32, i32* %i
  %.19 = add i32 %i.3, 1
  store i32 %.19, i32* %i
  br label %entry.endif.whilecond

entry.endif.endwhile:                             ; preds = %entry.endif.whilecond
  ret i32 0
}

; Function Attrs: argmemonly nounwind willreturn
declare void @llvm.memset.p0i8.i32(i8* nocapture writeonly, i8, i32, i1 immarg) #0

attributes #0 = { argmemonly nounwind willreturn }
