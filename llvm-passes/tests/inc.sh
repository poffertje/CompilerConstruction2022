#
# Included by run scripts in subdirectories - do not run directly!
#

function echo_success {
    echo -e '\033[27;32m'"\033[1mok\033[0m"
}

function echo_failed {
    local suffix=$1
    echo -e '\033[27;31m'"\033[1mfailed\033[0m ($suffix)"
}

# don't expand * if no files are found
shopt -s nullglob

# error on undefined variables and propagate error codes through pipes
set -uo pipefail

# stop on keyboard interrupt
trap 'exit 1' INT

# timeout before stopping the test
TIMEOUT=${TIMEOUT:-3}

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../.."
RUNTIMEDIR="$ROOT/runtime"

function run_test {
    local testfile=$1
    local passes=$2

    if [ $# -eq 3 ]; then
        local prefix=$3
        printf "%-60s " "$prefix$testfile:"
    else
        printf "%-60s " "$testfile:"
    fi


    # Wrap in subshell to disable "... Aborted" message
    $(timeout $TIMEOUT myopt $passes $testfile > "$testfile.optout" 2> "$testfile.opterr")

    RET=$?
    if [ $RET -eq 124 ]; then
        echo_failed "Timeout"
        return 1
    fi

    if [ ! $RET -eq 0 ]; then
        echo_failed "Error while running pass"
        return 1
    fi

    FileCheck "$testfile" < "$testfile.optout" 2> "$testfile.filecheckerr"

    if [ ! $? -eq 0 ]; then
        echo_failed "Wrong output IR"
        return 1
    fi

    echo_success
    rm "$testfile.optout" "$testfile.opterr" "$testfile.filecheckerr"
    return 0
}

function run_test_dynamic {
    local testfile=$1
    local passes=$2

    if [ $# -eq 3 ]; then
        local prefix=$3
        printf "%-60s " "$prefix$testfile:"
    else
        printf "%-60s " "$testfile:"
    fi

    ( frontend "$testfile" -I "$RUNTIMEDIR"/ -o- |
      myopt -alloca-hoisting -mem2reg $passes -o "$testfile.optout" &&
      llvm-link "$testfile.optout" "$RUNTIMEDIR"/obj/*.ll |
      llc -filetype=obj -o "$testfile.obj" &&
      clang -o "$testfile.bin" "$testfile.obj") 2> "$testfile.builderr"
    if [ ! $? -eq 0 ]; then
        echo_failed "Error while building"
        return 1
    fi

    "./$testfile.bin" > "$testfile.out" 2> "$testfile.err"

    if ! grep "YES" "$testfile.out" >/dev/null; then
        echo_failed "Crashed before check"
        return 1
    fi
    if grep "NO" "$testfile.out" >/dev/null; then
        echo_failed "Check failed"
        return 1
    fi

    echo_success
    rm "$testfile.optout" "$testfile.obj" "$testfile.bin" "$testfile.builderr" \
        "$testfile.out" "$testfile.err"
    return 0
}
