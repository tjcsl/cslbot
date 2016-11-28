#!/bin/bash
export MYPYPATH=test/stubs
echo "Checking static types..."
mypy --disallow-untyped-calls --strict-optional .
