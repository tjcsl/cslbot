#!/bin/bash
export MYPYPATH=test/stubs
echo "Checking static types"
mypy cslbot scripts test
