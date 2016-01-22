#!/bin/bash
set -e
gen_input() {
    files=`find cslbot/commands/*.py -not -name __init__.py -printf '%f\n'`
    names=`for x in $files; do echo $x|sed s/\.py//; done`
    mkdir fuzz_input
    for x in $names; do
        echo '!'$x > fuzz_input/$x
    done
}
test -d fuzz_input || gen_input
py-afl-fuzz -m 200MB -i fuzz_input -o fuzz_output -- `which python` ./scripts/fuzz.py
