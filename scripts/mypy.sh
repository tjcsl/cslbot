#!/bin/bash
export MYPYPATH=test/stubs
echo "Checking static types..."
env python3 -m mypy --strict \
    --allow-untyped-defs \
    --allow-untyped-calls \
    --allow-incomplete-defs \
    --allow-any-generics \
    --no-check-untyped-defs .
