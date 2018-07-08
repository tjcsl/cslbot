#!/bin/bash
set -euo pipefail
tweepy_path=$(find -name 'tweepy' -print | grep site-packages | head -n 1)

if [ -z ${tweepy_path} ]
then
  echo "WARNING: tweepy not found, fixer exiting"
  exit 1
fi

cd $tweepy_path

for file in $(find -iname '*.py')
do
  sed -i 's/async/async_/g' $file
done
