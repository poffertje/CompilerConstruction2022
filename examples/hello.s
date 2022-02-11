	.text
	.file	"<string>"
	.globl	main                    # -- Begin function main
	.p2align	4, 0x90
	.type	main,@function
main:                                   # @main
	.cfi_startproc
# %bb.0:                                # %entry
	nop
	nop
	nop
	pushq	%rax
	.cfi_def_cfa_offset 16
	movl	%edi, 4(%rsp)
	movl	$.str.0, %edi
	nop
	callq	puts
	nop
	nop
	nop
	nop
	nop
	xorl	%eax, %eax
	popq	%rcx
	.cfi_def_cfa_offset 8
	retq
.Lfunc_end0:
	.size	main, .Lfunc_end0-main
	.cfi_endproc
                                        # -- End function
	.type	.str.0,@object          # @.str.0
	.section	.rodata.str1.1,"aMS",@progbits,1
	.globl	.str.0
.str.0:
	.asciz	"Hello, World!"
	.size	.str.0, 14

	.section	".note.GNU-stack","",@progbits
