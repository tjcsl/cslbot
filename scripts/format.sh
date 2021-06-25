#!/bin/bash
autopep8 -ir -aaa -j 0 --experimental .
yapf -irp .
isort .
