FenneC compiler frontend
========================

The frontend consists of a number of phases that gradually transform a source
program into LLVM IR. It can be invoked as `python3 main.py` or as `frontend`
if the pythonenv is loaded. main.py invokes the C preprocessor (see below),
calls all the compilation phases in sequence, pretty-prints errors, and handles
I/O stuff like output filenames and stdin/stdout support. It also offers some
handy command-line options for debugging (see below).


Phase 1 - Lexing
----------------

First, the input file is tokenized by the lexer in lexer.py. The lexer is built
using the PLY library for which the documentation can be found
[here](http://www.dabeaz.com/ply/ply.html). To see how the input is tokenized
without sending the tokens to the parser, run lexer.py directly:

    $ echo "int i = 1;" | python3 lexer.py
    LexToken(TYPE,'int',1,0)
    LexToken(ID,'i',1,4)
    LexToken(ASSIGN,'=',1,6)
    LexToken(INTCONST,'1',1,8)
    LexToken(SEMICOL,';',1,9)


Phase 2 - Parsing
-----------------

After tokenization, the tokens are parsed according to the grammar from the
FenneC Language Reference. parser.py implements this grammar (also using PLY),
producing an Abstract Syntax Tree (AST) of the source code. The AST definition
is in ast.py (you can ignore all the boilerplate code before `class
Program(Node):`) and adheres closely to the names used in the language
reference.

In order to produce descriptive error messages when processing the AST in later
phases, AST nodes must know about the source locations (filename, line number,
column number) of the source code elements they represent. The parser is
responsible for annotating them with this information, for which it uses the
`loc` helper function (documented in parser.py). For example, the following
snippet binds the source location of production rule `p` to a newly created
`Program` AST node:

    def p_program(p):
        '''program : declarations'''
        p[0] = ast.Program(p[1]).at(loc(p))

All AST node definitions in ast.py have `children` and `types` attributes.
`children` tells the parent class `Node` to which attributes constructor
arguments must be assigned. For instance, `Program` only has a `declarations`
child, which means that `p[1]` in the snippet above is stored in
`p[0].declarations`. `types` is used during AST verification which is done
automatically after each phase to check if a bug in the compiler produced an
incorrect AST. The type of the `declarations` attribute is `Declaration+`,
which means "a non-empty list of `Declaration` objects".

parser.py can be called as a standalone binary in order to test your grammar.
When called directly, it reads .fc code from stdin and pretty-prints the
resulting AST to stdout. It enables PLY's debug mode which makes it output any
conflicts. Thisi also makes it produce a file called parser.out with details of
the generated state machine, including a detailed description of where
conflicts occur.


Phase 3 - Desugaring
--------------------

Some syntax features in FenneC are "syntactic sugar": shorthands for things you
can also write in a longer way. For instance, `i += 1` is the same as `i = i +
1`. In order to reduce effort for later phases (i.e., not having to duplicate
code for both cases in the rest of the compiler), we transform these syntactic
shorthands into their equivalent counterparts during a process called
"desugaring":

1. Modification statements such as `i += 1` are rewritten to regular
   assignments with a binary operator in the right-hand side, such as
   `i = i + 1`.

2. For-loops are expanded to while-loops where the induction variable is defined
   as a regular variable, and explicitly incremented by one during each loop
   iteration. For-loops in FenneC are very simple and constrained, so the
   transformation is straight-forward. The transformation must guarantee that
   the start and stop expressions are both evaluated exactly once. It must also
   make sure that the induction variable name does not clash with other
   variables in the scope.

When desugaring, the source program has not been checked for scoping/type
errors yet. So when transforming AST nodes, the source location annotations are
copied to the newly created nodes to be able to produce meaningful error
messages on them later. This is again done by calling `at` on an AST node, but
now with another node as argument: `newnode.at(oldnode)`.


Phase 4 - Context analysis
--------------------------

Context analysis is implemented in context.py, its job is to bind variable uses
and function calls to their corresponding variable/function definitions. It
does this according to the scoping rules in the language reference. The
reference document explains how the scoping rules are best implemented using a
stack of scoping levels, which is exactly what context.py does: it maintains a
stack of lookup tables, pushing a new table for each code block that defines a
new scope. At each variable/function definition, it adds the definition to the
scope on top of the stack after checking for duplicates. At each variable use
or function call, it tries to find a definition in one of the stack levels.


Phase 5 - Type checking
-----------------------

This phase performs a large number of checks on the types of nodes in the AST.
Type restrictions listed in the language reference are implemented here. This
includes restricting operand types for different operators, checking the
number of arguments in a function call and their types, checking is assigned
variables match the variable type, etc..

The grammar language reference is actually slightly more restrictive than
implemented in the parser phase, in that it parses `void` as a type everywhere
rather than only as function return type. The type checker therefore must check
if `void` is not used in any other places. This design is intentional, because
type error messages are generally more descriptive than parser errors.

The type checker annotates all expressions with their type in a `ty` attribute.


Phase 6 - IR generation
-----------------------

When the AST has been desugared and checked to be a valid program, it is
transformed into LLVM IR by irgen.py. The LLVM IR language is well-documented
[here](http://releases.llvm.org/10.0.1/docs/LangRef.html), make sure to read
that before modifying this phase. We use llvmlite Python bindings for LLVM,
which has a great [user
guide](https://llvmlite.readthedocs.io/en/v0.34.0/user-guide/).

irgen.py transforms the AST `Program` node into an LLVM module. Most AST nodes
map trivially to an LLVM counterpart: only binary logical operators `&&` and
`||` are hard cases because they require lazy evaluation of their operands. You
are encouraged to read the existing code to see which LLVM instructions are used
(and to look them up in the LLVM language reference). A few concepts that are
covered in the lecture recur here:

- LLVM IR is in Static Single Assignment (SSA) form, meaning that every value
  is only defined once and cannot be reassigned afterwards. Intuitively, this
  poses a problem for variables, which can be reassigned multiple times in
  FenneC.  However, we simply transform each variable into an `alloca` which
  makes it a memory location (which are not single-assignments) and then store
  multiple times to that. We rely on LLVM's `mem2reg` pass to transform the
  variables into nice SSA instructions with phi nodes where possible.

- LLVM IR functions consist of basic blocks, which consist of instructions.
  Branches at the end of basic blocks implement control flow. All control flow
  statements (if-else and loops) in FenneC must be mapped to theses branches and
  basic blocks.

To build IR instructions, we make use of an `IRBuilder`. There is also a C++
variant of this class that you will be using later in the course, so you should
familiarize yourself with how it works. An IR builder positions itself at a
position in a basic block, and emits instructions there. The result of an
emitted instruction is often used as an operand for the next emitted
instruction.


Command-line usage
------------------

main.py (or `frontend`) has a number of command line options to help debugging.
See `frontend -h` for a full description, but here are some examples:

- `--dump-after PHASE` makes the compiler only run up to the specified phase
  and pretty-print the AST at that point. E.g., specify `desugar` to see if the
  desuring routine you just implemented works as you expected.

- `--verbose` pretty-prints the AST after every phase, and prints the generated
  IR to stdout.

- `-I` adds an include directory to the preprocessor (tells it where to look
  for `#include` files).

- By default, the frontent emits a .ll file containing human-readable LLVM
  code. `--emit-bc` makes it emit a binary bitcode file with the .bc extension
  instead.

- If no input file is given, the compiler reads from stdin and writes to
  stdout.

To get to an executable binary, the LLVM code in the .ll file produced by the
frontend needs to be assembled and linked. This is easily done using `llc` and
`clang`:

    $ frontend -o foo.ll foo.fc   # LLVM bitcode
    $ llc -o foo.o foo.ll         # target object file, e.g. x86
    $ clang -o foo foo.o          # target binary

Exactly these steps are present in the Makefile for convenience, the three
commands above can be replaced with:

    $ make foo

Which compiles foo.fc to a binary called "foo".

For the experts: we could also use `ld` for linking, but the advantage of
`clang` is that it adds the libc startup code that calls `main`. You could also
write a FenneC program that defines a custom `void _start` and link it with `ld`.


Utility functions
-----------------

util.py contains some utility classes that are used throughout the rest of the
code. Most notably, it implements two AST traversal base classes:

- `ASTVisitor` defines a base class for traversing the AST, this is used during
  context analysis and type checking. It allows you to specify custom behaviour
  for any AST node by defining a `visit<node-name>` method, e.g.,
  `def visitProgram(self, program): ...`. By default, the visitor visits all
  child nodes of a node.

- `ASTTransformer` is similar to `ASTVisitor`, but it also allows methods to
  return a value that replace the node as a child of its parent. This is used
  during desugaring and IR generation.

- `NodeError` allows you to raise an exception on an AST node, resulting in a
  pretty-printed error message displaying that node's location in the original
  source file.


Tests
-----

The compiler comes with a built-in test suite in the `test/` directory. The
testsuite is invoked by running `make check` or `./runtests.py` inside the
frontend directory, or `make check-frontend` in the root directory. The tests
are divided into two levels of directories: phases first, test type second. You
can, and are encouraged to, add more tests to these directories as you develop
new compiler features. Each test is a small .fc file that tests an isolated
aspect of the compiler (try to look at the existing tests for inspiration).
Newly added .fc files are automatically found by the testrunner. Possible phases
are preprocess/parser/desugar/context/typecheck/irgen. Test types are one of the
following:

- `success` checks if the compiler has not produced an error after the
  specified phase (i.e., it has a zero exit code after `--dump-after PHASE`).

- `error` asserts that the compiler has produced an error after the specified
  phase (i.e., it has a nonzero exit code).

- `dump` dumps the AST after the specified phase and compares the output to an
  expected result. The expected result for phase/dump/file.fc must be put in
  phase/dump/file-expect.fc.

- `run` compiles the source program and links the result to produce a binary
  with Clang. It then runs that binary (without any command-line arguments) and
  compares the result against an expected outcome. The expected output for
  test/phase/run/file.fc must be in test/phase/run/file.out.

- `run-group` is a special case of `run` that requires multiple source files to
  be linked together. Each testcase is a subdirectory of `run-group` containing
  .fc files to be compiled and linked, and a file called expected.out
  containing the expected output after running the resulting binary. See
  `test/irgen/run-group/hello/` for an example.
