#!/bin/bash
shopt -s extglob
find -name "*.py" | xargs black -l 100
