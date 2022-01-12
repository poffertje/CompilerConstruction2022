LLVM IR passes
==============

This directory contains all LLVM passes in the framework. Some example passes
are provided, and any .cpp file you place here will automatically be included.
These passes transform LLVM IR and come with a number of tests (see below). The
full-program examples can also be built using these passes (see
examples/README.md). It is also possible to manually invoke passes for testing
as explained below.


Example passes
--------------

The framework comes with 3 passes currently: `DummyPass.cpp`, `DummyDTPass.cpp`
and `DummyModulePass.cpp`. We strongly recommend you read these files and use
them as a starting point for your own passes. The first two are used for
Assignment 2, whereas the last one is only used for Assignment 3.


Utilities
---------

The framework comes with a number of utility features and functions, which can
be found in `utils.h` and `utils.cpp`. In particular, you will notice all passes
include only `utils.h`. Inside this header file all C++ and LLVM includes occur.
The header file defines a number of macro's useful for output and debugging:

 - `LOG_LINE` outputs a line, for example `LOG_LINE("Instruction " << *I << "
   has operand " << *I->getOperand(0));`
 - `DEBUG_LINE` is similar to `LOG_LINE`, but only runs when the `-debug` or
   `-debug-only` argument is passed to `myopt`.
 - `ERROR` is similar to `LOG_LINE` but exits the program immediately afterward.

The utility functions are primarily useful for Assignment 3. The
`shouldInstrument` function says whether to perform transformation on a given
function. It will skip helper functions and forward declarations for instance.
The `addParamsToFunction` is described in the Assignment 3 pdf.


Tests
-----

This directory also contains a testing infrastructure for the passes. Most tests
are static ones: they consist of some annotated LLVM IR. This IR is run through
the pass that is being tested, and the annotations tell the checker what the
pass should have changed. For Assignment 3 (the bounds checker) there are also a
number of dynamic tests, where the provided IR is actually compiled into a
binary and executed, to check whether at runtime it shows the correct behavior.

All tests are already present in the framework, and can be used with `make
check-passes` from the top directory of the framework. The run script will
automatically detect which passes you have actually implemented - if a set of
tests is not running whereas you expected it to, check to see if you named your
pass correctly.

You are strongly encouraged to look at the existing tests and *write your own*
to cover more corner cases. You can look at any .ll file in the tests/adce
directory for instance to see how this works. The tests are written with the
same tool that's used for testing LLVM itself:
[FileCheck](https://llvm.org/docs/CommandGuide/FileCheck.html). The IR is run
through opt with the relevant pass, and the comments contain annotations which
lines should be present in the output IR. Refer to the FileCheck documentation
for more details.


Debugging failing tests
-----------------------

If a test fails it will leave behind a number of intermediate output files to
help you debug the issue. A fail can be of several reasons, for static tests
these are: "Error while running pass" and "Wrong output IR". For this
explanation we will consider the test adce/dead_load.ll as a running example.

The first error means that while compiling the IR, your pass crashed. You can
find the output of opt in the .opterr file (e.g., adce/dead_load.ll.opterr). Any
output from your pass (e.g., LOG_LINE and value dumps) are present in this file
and should help you find the issue. Optionally you can manually invoke the pass
outside of the testing infrastructure as described below.

If compilation is successful the resulting IR is placed in a .optout file (e.g.,
adce/dead_load.ll.optout). It is then run through FileCheck, which outputs any
error in a .filecheckerr file (e.g., adce/dead_load.ll.filecheckerr). FileCheck
scans for every `CHECK` line in your IR (in the .optout file), and verbosely
outputs what it could not find in the case of an error.

All intermediate files are automatically removed if a test succeeds.


Manually invoking passes with opt
---------------------------------

Most of the time you do not have to invoke passes manually, as running the tests
or examples (see examples/README.md) will do this for you. If you are debugging
a specific case it might be easier to manually run your pass though, which you
can do with the `myopt` command. `myopt` is a wrapper around the `opt` command
LLVM provides, which simply loads the passes you have written into its memory,
so you can invoke them if you want.

An example usage of `myopt` could be as follows:

    $ myopt foo.ll -coco-constprop -coco-adce

This will show the resulting IR on screen. Any pass can be invoked like this,
and `myopt` will execute them in the specified order. A single pass can occur
multiple times, and LLVM will execute it every time. You can also specify
built-in LLVM passes (e.g., `-constprop` and `-adce` invoke the internal LLVM
implementations of these algorithms).

