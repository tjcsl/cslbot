#!/bin/bash
cd $(dirname $0)
sphinx-apidoc-python3.3 -H IrcBot -f -o doc .
sphinx-build-python3.3 -b html doc gh-pages
