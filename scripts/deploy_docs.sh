#!/bin/bash
if [ "$TRAVIS_PULL_REQUEST" == "false" ] && [ "$TRAVIS_BRANCH" == "master" ]; then
  echo "Pushing docs to Github Pages"

  git config --global user.email "tjhsstBot@tjhsst.edu"
  git config --global user.name "tjhsstBot"

  git clone --depth=50 --branch=gh-pages https://${GH_TOKEN}@github.com/tjcsl/cslbot.git gh-pages
  latest=$(git log -1 --pretty=%s|sed "s/Update docs, build \([0-9]\+\)/\1/")
  if [ "$latest" -gt "$TRAVIS_BUILD_NUMBER" ]; then
      echo "Not overwriting newer docs."
      exit
  fi
  rm -rf gh-pages/*
  cd gh-pages
  cp -r ../doc/build/* .
  git add -A .
  git commit -m "Update docs, build $TRAVIS_BUILD_NUMBER"
  git push origin gh-pages |& sed s/${GH_TOKEN}/[secure]/g
  echo "Pushed docs to Github Pages"
fi
