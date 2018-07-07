#!/bin/bash
export MYPYPATH=test/stubs
echo "Checking static types..."
env python3 -m mypy --python-version 3.7 --incremental --disallow-untyped-calls --warn-return-any .
