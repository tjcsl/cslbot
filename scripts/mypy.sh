#!/bin/bash
export MYPYPATH=test/stubs
echo "Checking static types..."
env python3 -m mypy .
