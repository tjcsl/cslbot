#!/bin/bash
cd $(dirname $0)/..
sphinx-apidoc -H IrcBot -f -o doc .
sphinx-build -W doc doc/build
