#!/usr/bin/env bash

# cd to test dir
cd "$(dirname "${BASH_SOURCE[0]}")"

source ../inc.sh

nfail=0
for tfile in *.ll; do
    if ! run_test "$tfile" "-loop-simplify -alloca-hoisting -mem2reg -coco-licm"; then
        nfail=$((nfail + 1))
    fi
done

exit $nfail
