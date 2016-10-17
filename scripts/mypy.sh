#!/bin/bash
export MYPYPATH=test/stubs
echo "Checking static types..."
mypy --incremental --disallow-untyped-calls .
