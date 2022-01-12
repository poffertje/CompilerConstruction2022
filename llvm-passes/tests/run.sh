#!/usr/bin/env bash
TESTPASSES="adce licm constprop boundscheck"

num_success=0
num_fail=0
num_skipped=0

# cd to test dir
cd "$(dirname "${BASH_SOURCE[0]}")"

# don't expand * if no files are found
shopt -s nullglob

# error on undefined variables and propagate error codes through pipes
set -uo pipefail

# stop on keyboard interrupt
trap 'exit 1' INT

for testpass in $TESTPASSES; do
    echo
    echo "### Running tests for $testpass"
    echo

    pass="-coco-$testpass"
    o=`echo "" | myopt $pass 2>&1 >/dev/null`
    if [ ! $? -eq 0 ]; then
        echo "$o" | grep "Unknown command line argument '$pass'" >/dev/null
        if [ $? -eq 0 ]; then
            echo "Skipping $testpass - not implemented"
            num_skipped=$((num_skipped + 1))
            continue
        fi
    fi

    ./$testpass/run.sh
    if [ $? -eq 0 ]; then
        num_success=$((num_success + 1))
    else
        num_fail=$((num_fail + 1))
    fi
done

echo "$num_success passes succeeded, $num_fail failed, $num_skipped skipped"
