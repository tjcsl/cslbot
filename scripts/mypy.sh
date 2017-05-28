#!/bin/bash
export MYPYPATH=test/stubs
echo "Checking static types..."
mypy --python-version 3.6 --incremental --disallow-untyped-calls --warn-return-any .
