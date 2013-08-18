#!/bin/bash
files=`find /home/peter/ircbot/ -type d -or -type f -and -not -name fixperms.sh`
chown peter:ircbot $files
chmod g+rw $files
