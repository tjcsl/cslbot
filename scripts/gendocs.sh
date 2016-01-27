#!/bin/bash
set -e
cd $(dirname $0)/..
sphinx-apidoc -H IrcBot -f -o build/.tmp cslbot
rsync --checksum build/.tmp/*.rst doc/
sphinx-build -W doc -d build/sphinx/doctrees build/sphinx/html
if ! [ -z "`git status --porcelain`" ]; then
    echo "Modified files found, did you add a module?"
    git status --porcelain
    exit 1
fi
