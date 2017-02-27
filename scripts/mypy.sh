#!/bin/bash
export MYPYPATH=test/stubs
echo "Checking static types..."
# FIXME: Make strict validation work.
mypy --python-version 3.6 --strict --no-check-untyped-defs --allow-untyped-defs --no-strict-boolean --no-warn-return-any .
