" Vim syntax file
" Language:	FenneC
" Filenames:	*.fc *.fh
" Maintainer:	Koen Koning <koen.koning@vu.nl>
" Last Change:	2017 Nov 24
"
" Based on the Vim 8.0 C syntax file

" Quit when a (custom) syntax file was already loaded
if exists("b:current_syntax")
  finish
endif

" Keywords for control flow
syn keyword	fcStatement	break return continue
syn keyword	fcConditional	if else
syn keyword	fcRepeat	while for do to

" Comments
syn keyword	fcTodo		contained TODO FIXME XXX
syn cluster	fcCommentGroup	contains=fcTodo
syn region	fcCommentL	start="//" skip="\\$" end="$" keepend contains=@fcCommentGroup,Spell
syn region	fcComment	matchgroup=cCommentStart start="/\*" end="\*/" contains=@fcCommentGroup,fcCommentStartError,Spell extend
syn match	fcCommentError	display "\*/"
syn match	fcCommentStartError display "/\*"me=e-1 contained

" String and char constants
syn match	fcSpecial	display contained "\\\(x\x\+\|\o\{1,3}\|.\|$\)"
syn match	fcFormat	display "%\(\d\+\$\)\=[-+' #0*]*\(\d*\|\*\|\*\d\+\$\)\(\.\(\d*\|\*\|\*\d\+\$\)\)\=\([hlL]\|ll\)\=\([bdiuoxXDOUfeEgGcCsSpn]\|\[\^\=.[^]]*\]\)" contained
syn match	fcFormat	display "%%" contained
syn region	fcString	start=+L\="+ skip=+\\\\\|\\"+ end=+"+ contains=fcSpecial,fcFormat,@Spell extend
syn match	fcCharacter	"'[^\\]'"

" Number constants
syn case ignore
syn match	fcNumbers	display transparent "\<\d\|\.\d" contains=fcNumber,fcFloat
syn match	fcNumbersCom	display contained transparent "\<\d\|\.\d" contains=fcNumber,fcFloat
syn match	fcNumber	display contained "\d\+\>"
syn match	fcNumber	display contained "0x\x\+\>"
syn match	fcFloat		display contained "\d\+\.\d*"
syn match	fcFloat		display contained "\.\d\+\>"
syn case match

" Bool constants
syn keyword     fcBool      true false

" Blocks
syn region	fcBlock		start="{" end="}" transparent fold

" Types
syn keyword	fcType		bool char int float void

" Modifiers for globals
syn keyword	fcStorageClass	extern static

" Includes
syn region	fcIncluded	display contained start=+"+ skip=+\\\\\|\\"+ end=+"+
syn match	fcIncluded	display contained "<[^>]*>"
syn match	fcInclude	display "^\s*\zs#\s*include\>\s*["<]" contains=fcIncluded


" Define the default highlighting.
" Only used when an item doesn't have highlighting yet
hi def link fcFormat		fcSpecial
hi def link fcCommentL		fcComment
hi def link fcCommentStart	fcComment
hi def link fcConditional	Conditional
hi def link fcRepeat		Repeat
hi def link fcCharacter		Character
hi def link fcNumber		Number
hi def link fcFloat		Float
hi def link fcCommentError	fcError
hi def link fcCommentStartError	fcError
hi def link fcStorageClass	StorageClass
hi def link fcInclude		Include
hi def link fcIncluded		fcString
hi def link fcError		Error
hi def link fcStatement		Statement
hi def link fcType		Type
hi def link fcBool		Constant
hi def link fcString		String
hi def link fcComment		Comment
hi def link fcSpecial		SpecialChar
hi def link fcTodo		Todo

let b:current_syntax = "fennec"
" vim: ts=8
