#!/bin/bash
set -e
cd $(dirname $0)/..
sphinx-apidoc -H IrcBot -f -o doc cslbot
sphinx-build -W doc doc/build
if ! [ -z "`git status --porcelain`" ]; then
    echo "Modified files found, did you add a module?"
    exit 1
fi
