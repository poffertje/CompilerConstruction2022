#!/usr/bin/env bash

# cd to test dir
cd "$(dirname "${BASH_SOURCE[0]}")"

source ../inc.sh

# Perform static tests: compile IR snippets and statically check the resulting
# IR for presence of bounds checks.
cd static
nfail=0
for tfile in *.ll; do
    if ! run_test $tfile -coco-boundscheck static/; then
        nfail=$((nfail + 1))
    fi
done
cd ..

# The dynamic tests are full programs that are actually linked into binaries,
# where we check the output by running them, to see if the bounds checker
# correctly detects out-of-bound accesses.
cd dynamic
for tfile in *.fc; do
    if ! run_test_dynamic $tfile -coco-boundscheck dynamic/; then
        nfail=$((nfail + 1))
    fi
done
cd ..

exit $nfail
