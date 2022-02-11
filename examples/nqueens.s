	.text
	.file	"<string>"
	.globl	printArray              # -- Begin function printArray
	.p2align	4, 0x90
	.type	printArray,@function
printArray:                             # @printArray
	.cfi_startproc
# %bb.0:                                # %entry
	nop
	nop
	nop
	nop
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	pushq	%r14
	pushq	%rbx
	subq	$16, %rsp
	.cfi_offset %rbx, -32
	.cfi_offset %r14, -24
	movq	%rsi, %r14
	movl	%edi, -24(%rbp)
	movl	$0, -20(%rbp)
	jmp	.LBB0_1
	.p2align	4, 0x90
.LBB0_8:                                # %entry.whilebody.endwhile
                                        #   in Loop: Header=BB0_1 Depth=1
	movl	$.str.3, %edi
	xorl	%eax, %eax
	nop
	nop
	nop
	nop
	callq	printf
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	incl	-20(%rbp)
.LBB0_1:                                # %entry.whilecond
                                        # =>This Loop Header: Depth=1
                                        #     Child Loop BB0_3 Depth 2
	movl	-20(%rbp), %eax
	cmpl	-24(%rbp), %eax
	jge	.LBB0_9
# %bb.2:                                # %entry.whilebody
                                        #   in Loop: Header=BB0_1 Depth=1
	movq	%rsp, %rax
	leaq	-16(%rax), %rbx
	movq	%rbx, %rsp
	movl	$0, -16(%rax)
	jmp	.LBB0_3
	.p2align	4, 0x90
.LBB0_6:                                # %entry.whilebody.whilebody.else
                                        #   in Loop: Header=BB0_3 Depth=2
	movl	$.str.1, %edi
.LBB0_7:                                # %entry.whilebody.whilebody.endif
                                        #   in Loop: Header=BB0_3 Depth=2
	xorl	%eax, %eax
	nop
	callq	printf
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	movl	$.str.2, %edi
	xorl	%eax, %eax
	nop
	callq	printf
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	incl	(%rbx)
.LBB0_3:                                # %entry.whilebody.whilecond
                                        #   Parent Loop BB0_1 Depth=1
                                        # =>  This Inner Loop Header: Depth=2
	movl	(%rbx), %eax
	cmpl	-24(%rbp), %eax
	jge	.LBB0_8
# %bb.4:                                # %entry.whilebody.whilebody
                                        #   in Loop: Header=BB0_3 Depth=2
	movl	(%rbx), %eax
	movslq	-20(%rbp), %rcx
	cmpl	(%r14,%rcx,4), %eax
	jne	.LBB0_6
# %bb.5:                                # %entry.whilebody.whilebody.if
                                        #   in Loop: Header=BB0_3 Depth=2
	movl	$.str.0, %edi
	jmp	.LBB0_7
.LBB0_9:                                # %entry.endwhile
	movq	%rsp, %rax
	leaq	-16(%rax), %rbx
	movq	%rbx, %rsp
	movl	$0, -16(%rax)
	.p2align	4, 0x90
.LBB0_10:                               # %entry.endwhile.whilecond
                                        # =>This Inner Loop Header: Depth=1
	movl	-24(%rbp), %eax
	addl	%eax, %eax
	cmpl	%eax, (%rbx)
	jge	.LBB0_12
# %bb.11:                               # %entry.endwhile.whilebody
                                        #   in Loop: Header=BB0_10 Depth=1
	movl	$.str.4, %edi
	xorl	%eax, %eax
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	callq	printf
	nop
	nop
	nop
	incl	(%rbx)
	jmp	.LBB0_10
.LBB0_12:                               # %entry.endwhile.endwhile
	movl	$.str.5, %edi
	xorl	%eax, %eax
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	callq	printf
	nop
	nop
	nop
	nop
	nop
	nop
	leaq	-16(%rbp), %rsp
	popq	%rbx
	popq	%r14
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	nop
	nop
	retq
.Lfunc_end0:
	.size	printArray, .Lfunc_end0-printArray
	.cfi_endproc
                                        # -- End function
	.globl	getPositions            # -- Begin function getPositions
	.p2align	4, 0x90
	.type	getPositions,@function
getPositions:                           # @getPositions
	.cfi_startproc
# %bb.0:                                # %entry
	nop
	nop
	nop
	nop
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	pushq	%r14
	pushq	%rbx
	subq	$16, %rsp
	.cfi_offset %rbx, -32
	.cfi_offset %r14, -24
	movq	%rsi, %r14
	movl	%edi, -24(%rbp)
	movl	%edx, -20(%rbp)
	movl	%ecx, -28(%rbp)
	movslq	%edx, %rax
	movl	%ecx, (%rsi,%rax,4)
	movl	-24(%rbp), %eax
	decl	%eax
	cmpl	%eax, -20(%rbp)
	jne	.LBB1_3
# %bb.1:                                # %entry.if
	movl	-24(%rbp), %edi
	movq	%r14, %rsi
	nop
	callq	printArray
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
.LBB1_2:                                # %entry.endif.endwhile
	leaq	-16(%rbp), %rsp
	popq	%rbx
	popq	%r14
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.LBB1_3:                                # %entry.endif
	.cfi_def_cfa %rbp, 16
	movq	%rsp, %rax
	leaq	-16(%rax), %rbx
	movq	%rbx, %rsp
	movl	$0, -16(%rax)
	jmp	.LBB1_4
	.p2align	4, 0x90
.LBB1_12:                               # %entry.endif.whilebody.endwhile
                                        #   in Loop: Header=BB1_4 Depth=1
	cmpl	$0, (%rax)
	je	.LBB1_13
.LBB1_14:                               # %entry.endif.whilebody.endwhile.endif
                                        #   in Loop: Header=BB1_4 Depth=1
	incl	(%rbx)
.LBB1_4:                                # %entry.endif.whilecond
                                        # =>This Loop Header: Depth=1
                                        #     Child Loop BB1_6 Depth 2
	movl	(%rbx), %eax
	cmpl	-24(%rbp), %eax
	jge	.LBB1_2
# %bb.5:                                # %entry.endif.whilebody
                                        #   in Loop: Header=BB1_4 Depth=1
	movq	%rsp, %rcx
	leaq	-16(%rcx), %rax
	movq	%rax, %rsp
	movl	$0, -16(%rcx)
	movq	%rsp, %rdx
	leaq	-16(%rdx), %rcx
	movq	%rcx, %rsp
	movl	$0, -16(%rdx)
	jmp	.LBB1_6
	.p2align	4, 0x90
.LBB1_11:                               # %entry.endif.whilebody.whilebody.endif
                                        #   in Loop: Header=BB1_6 Depth=2
	incl	(%rcx)
.LBB1_6:                                # %entry.endif.whilebody.whilecond
                                        #   Parent Loop BB1_4 Depth=1
                                        # =>  This Inner Loop Header: Depth=2
	movl	-20(%rbp), %edx
	incl	%edx
	cmpl	%edx, (%rcx)
	jge	.LBB1_12
# %bb.7:                                # %entry.endif.whilebody.whilebody
                                        #   in Loop: Header=BB1_6 Depth=2
	movslq	(%rcx), %rdx
	movl	(%r14,%rdx,4), %esi
	movb	$1, %dl
	cmpl	(%rbx), %esi
	je	.LBB1_9
# %bb.8:                                # %no
                                        #   in Loop: Header=BB1_6 Depth=2
	movl	-20(%rbp), %edx
	movslq	(%rcx), %rsi
	subl	%esi, %edx
	incl	%edx
	imull	%edx, %edx
	movl	(%rbx), %edi
	subl	(%r14,%rsi,4), %edi
	imull	%edi, %edi
	cmpl	%edi, %edx
	sete	%dl
.LBB1_9:                                # %endcond
                                        #   in Loop: Header=BB1_6 Depth=2
	testb	%dl, %dl
	je	.LBB1_11
# %bb.10:                               # %entry.endif.whilebody.whilebody.if
                                        #   in Loop: Header=BB1_6 Depth=2
	movl	$1, (%rax)
	jmp	.LBB1_11
	.p2align	4, 0x90
.LBB1_13:                               # %entry.endif.whilebody.endwhile.if
                                        #   in Loop: Header=BB1_4 Depth=1
	movl	-24(%rbp), %edi
	movl	-20(%rbp), %edx
	incl	%edx
	movl	(%rbx), %ecx
	movq	%r14, %rsi
	nop
	callq	getPositions
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	jmp	.LBB1_14
.Lfunc_end1:
	.size	getPositions, .Lfunc_end1-getPositions
	.cfi_endproc
                                        # -- End function
	.globl	main                    # -- Begin function main
	.p2align	4, 0x90
	.type	main,@function
main:                                   # @main
	.cfi_startproc
# %bb.0:                                # %entry
	nop
	nop
	nop
	nop
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	pushq	%r15
	pushq	%r14
	pushq	%rbx
	pushq	%rax
	.cfi_offset %rbx, -40
	.cfi_offset %r14, -32
	.cfi_offset %r15, -24
	movl	%edi, -28(%rbp)
	cmpl	$2, %edi
	je	.LBB2_2
# %bb.1:                                # %entry.if
	movq	(%rsi), %rsi
	movl	$.str.6, %edi
	xorl	%eax, %eax
	nop
	callq	printf
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	movl	$1, %eax
	jmp	.LBB2_6
.LBB2_2:                                # %entry.endif
	movq	%rsp, %rbx
	leaq	-16(%rbx), %r15
	movq	%r15, %rsp
	movq	8(%rsi), %rdi
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	callq	atoi
	nop
	nop
	nop
                                        # kill: def $eax killed $eax def $rax
	movl	%eax, -16(%rbx)
	movl	%eax, %ecx
	movq	%rsp, %r14
	leaq	15(,%rcx,4), %rcx
	andq	$-16, %rcx
	subq	%rcx, %r14
	movq	%r14, %rsp
	leal	(,%rax,4), %edx
	movq	%r14, %rdi
	xorl	%esi, %esi
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	callq	memset
	nop
	nop
	nop
	nop
	nop
	nop
	movq	%rsp, %rax
	leaq	-16(%rax), %rbx
	movq	%rbx, %rsp
	movl	$0, -16(%rax)
	.p2align	4, 0x90
.LBB2_3:                                # %entry.endif.whilecond
                                        # =>This Inner Loop Header: Depth=1
	movl	(%rbx), %eax
	cmpl	(%r15), %eax
	jge	.LBB2_5
# %bb.4:                                # %entry.endif.whilebody
                                        #   in Loop: Header=BB2_3 Depth=1
	movl	(%r15), %edi
	movl	(%rbx), %ecx
	movq	%r14, %rsi
	xorl	%edx, %edx
	nop
	callq	getPositions
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	incl	(%rbx)
	jmp	.LBB2_3
.LBB2_5:                                # %entry.endif.endwhile
	xorl	%eax, %eax
.LBB2_6:                                # %entry.endif.endwhile
	leaq	-24(%rbp), %rsp
	popq	%rbx
	popq	%r14
	popq	%r15
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	nop
	nop
	nop
	nop
	retq
.Lfunc_end2:
	.size	main, .Lfunc_end2-main
	.cfi_endproc
                                        # -- End function
	.type	.str.0,@object          # @.str.0
	.section	.rodata.str1.1,"aMS",@progbits,1
	.globl	.str.0
.str.0:
	.asciz	"Q"
	.size	.str.0, 2

	.type	.str.1,@object          # @.str.1
	.globl	.str.1
.str.1:
	.asciz	"."
	.size	.str.1, 2

	.type	.str.2,@object          # @.str.2
	.globl	.str.2
.str.2:
	.asciz	" "
	.size	.str.2, 2

	.type	.str.3,@object          # @.str.3
	.globl	.str.3
.str.3:
	.asciz	"\n"
	.size	.str.3, 2

	.type	.str.4,@object          # @.str.4
	.globl	.str.4
.str.4:
	.asciz	"-"
	.size	.str.4, 2

	.type	.str.5,@object          # @.str.5
	.globl	.str.5
.str.5:
	.asciz	"\n"
	.size	.str.5, 2

	.type	.str.6,@object          # @.str.6
	.globl	.str.6
.str.6:
	.asciz	"Usage: %s <N>\n"
	.size	.str.6, 15

	.section	".note.GNU-stack","",@progbits
