Compiler Construction framework
===============================

Overview
--------

This is the framework documentation for Compiler Construction at the Vrije
Universiteit Amsterdam. During this course, students will develop compiler
features for a custom C-like language.

The framework consists of several parts:

- A compiler frontend, written in Python, that translates our C-like source
  language into LLVM IR which can be compiled to a binary using Clang.

- LLVM passes, written in C++, that optimize/instrument the IR.

- A runtime library, written in C, containing support code for instrumentation
  inserted by LLVM passes.

-  Tests for each part/assignments, and a number of test programs that can be
   instrumented with any LLVM pass.

Detailed documentation of these components resides in frontend/README.md,
llvm-passes/README.md and examples/README.md.


Getting started
---------------

First you need to install the dependencies (see below), which is done by
`bootstrap.sh`:

    $ bash bootstrap.sh

This script first installs some generic packages using the package manager
(`apt-get` on Ubuntu) which is why it asks for your sudo password. It then
downloads the necessary dependencies, builds them, and installs them into a
so-called pythonenv, which is basically just a directory containing binaries.
All files created by the bootstrap script are put in the `lib/` directory, so if
anything gets corrupted you can always remove this directory completely and
start over. To use the installed binaries and libraries after `bootstrap.sh` is
done, you need to add them to your environment variables. To do this, run:

    $ source shrc

If all goes well, this should add a "(coco)" prefix to your shell prompt. Now
you have access to all installed binaries, try it out like this:

    $ which clang
    /.../coco/lib/install/bin/clang

The pythonenv gives you access to the `frontend` command (which is simply a
shorthand for `python frontend/main.py`). This runs the compiler frontend on a
source file. Run the following command to see its options:

    $ frontend -h

Tests if it works by compiling a simple source file:

    $ frontend examples/hello.fc -I runtime
    $ clang -o examples/hello examples/hello.ll
    $ examples/hello
    Hello, World!

When you are done with your work, or you want access to your original system's
`clang`, for instance, you can get out of the pytonenv like this:

    $ deactivate

Before running bootstrap.sh, make sure you have enough disk space for
downloading and building LLVM. The entire `lib/` directory occupies about 2.7GB
or 5.4GB, depending if your system supports our prebuilt llvm (it most likely
does on Linux). Also take into account that building LLVM takes a long time,
and you probably don't want to do it on a laptop while running on battery.

In particular, we require the following dependencies:

- `build-essential` mainly for GNU Make (for the makefiles)
- Git and `wget` to fetch dependencies
- LLVM (version 5.0) as our compiler framework
- CMake and Ninja to build LLVM
- Python 3 for the frontend
- `llvmlite` for LLVM python bindings (used by frontend)
- `pythonenv` to install all dependencies into a local user directory


Using the Makefile
------------------

The root directory contains a `Makefile` which is used to build parts of the
compiler. It offers a number of commands:

    $ make passes           # build the passes
    $ make runtime          # build the runtime
    $ make check-frontend   # run frontend tests
    $ make check-passes     # run passes tests
    $ make examples         # build all examples (see examples/README.md)
    $ make example-$name    # build a single example (see examples/README.md)
    $ make handin-$num      # create tarball to handin on Canvas, per assignment
    $ make clean            # delete build files
    $ make cleaner          # delete all generated files, including lib/

Note that dependencies are automatically taken care of: the passes and runtime
will automatically rebuild when you run the tests or examples for instance.


Source directories
------------------

    lib/                    # dependencies, created by bootstrap.sh
    doc/                    # framework/language documentation
    frontend/               # frontend code (Assignment 1)
    frontend/README.md      # further documentation on frontend
    llvm-passes             # LLVM passes (Assignments 2 and 3)
    llvm-passes/README.md   # further documentation on passes
    runtime/                # runtime support code for passes
    examples/               # some example programs to test your compiler
    support/                # FenneC syntax highlighting files for Vim
    bootstrap.sh            # installs dependencies
    Makefile                # build commands, see previous section
    README.md               # this file
    shrc                    # script to load pythonenv
