FenneC example programs
=======================

This directory contains a number of example FenneC programs. You can use these
to test your compiler, and to draw inspiration on when writing your own
programs. You can place any FenneC (.fc) file in this directory and it can be
compiled by the framework.

Building and running
--------------------

From the root directory of the framework you can run `make examples` to build
all examples in this directory. You can also build a single example using `make
example-$name` (e.g., `make example-hello`). Building consists of a number of
steps:

1. Use the *frontend* to generate LLVM IR.
2. Run some basic passes to *prepare* the LLVM IR for later stages (see below).
3. Run your own passes using *opt*.
4. Link your program together with the *runtime*.
5. Compile the LLVM IR down to assembly.
6. Link the assembly into an executable binary.

All intermediate files are stored in the `obj/` directory. In particular, stages
1 through 4 produce LLVM IR that might be of interest while debugging your
compiler. The final binary is placed in the `bin/` directory. For example, if we
take `hello.fc`, compiling it will produce the following files:

	examples/obj/hello-1frontend.ll
	examples/obj/hello-2prep.ll
	examples/obj/hello-3opt.ll
	examples/obj/hello-4runtime.ll
	examples/obj/hello.o
	examples/bin/hello


To *run your own passes* on any of the test files, use the `PASSES=...` argument
of the makefile in the top directory of the framework. For example:

    $ make examples PASSES="-coco-constprop -coco-adce"
     # or to build only a single example program:
    $ make example-hello PASSES="-coco-constprop -coco-adce"

The passes your specify are passed down as-is to opt (`myopt` command), and can
thus contain any argument opt will understand, including any built-in LLVM pass.
These passes run in the order you specify them, and passes can occur multiple
times in the same command.

Once a program is built, it can be run as any normal program. For example:

    $ examples/bin/count 3
    num: 3
    3
    2
    1


Details of the build stages
---------------------------

The *frontend* takes a .fc file and runs the preprocessor (parsing any
`#include` directives, parses the file and finally produces LLVM IR. See
frontend/README.md for more details.

The *preparation* stage runs the passes specified in `OPTPREP`:
`alloca-hoisting` and `mem2reg`. Together these passes remove most `alloca`
instructions, promoting such stack variables to virtual register. This produces
LLVM IR that is in proper SSA form.

By default, the *opt* stage does nothing. By setting the `PASSES=...` variable
it will run any passes you specify. See above for more details.

The *runtime* contains helper functions and its LLVM IR is combined with the IR
of the program, see below for more details.

Runtime
-------

The runtime consist of a number of helper functions and can be found in the
runtime directory. The runtime also contains all *header files* that FenneC
uses. Currently there are two such files:

 - `stdlib.fh`: functions present in the runtime itself.
 - `cstdlib.fh`: prototypes for functions present in the C standard library.
   Most functions you are familiar with from C are compatible with FenneC,
   Examples include `printf`, `exit` and `atoi`.

The runtime implements two types of functions. First there are those that are
present in `stdlib.fh` and can be called directly from the FenneC code to
implement function the language doesn't support (e.g., casting integers to
floats). Secondly there are helper functions to which calls are inserted by
instrumentation. You will use this during Assignment 3, and an example is the
one used by DummyModulePass.

Programs
--------

A list of some of the programs included in this directory:

 - hello.fc: Hello, World!
 - doc-example.fc: the example given in the langref demonstrating some features
 - count.fc: a program that counts down
 - nqueens.fc: solves the n-queens chessboard puzzle
 - pi.fc: a pi approximate using monte carlo method
 - qsort.fc: a quicksort implementation

