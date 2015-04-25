#!/bin/bash
if [ "$TRAVIS_PULL_REQUEST" == "false" ] && [ "$TRAVIS_BRANCH" == "master" ]; then
  echo "Pushing docs to Github Pages"

  git config --global user.email "tjhsstBot@tjhsst.edu"
  git config --global user.name "tjhsstBot"

  git clone --depth=50 --branch=gh-pages https://${GH_TOKEN}@github.com/tjcsl/cslbot.git gh-pages
  rm -rf gh-pages/*
  cd gh-pages
  cp -r ../doc/build/* .
  git add -A .
  latest=$(git log -1 --pretty=%s|sed "s/Update docs, build \([0-9]\+\)/\1/")
  git commit -m "Update docs, build $TRAVIS_BUILD_NUMBER"
  if [ "$latest" -ge "$TRAVIS_BUILD_NUMBER" ]; then
      echo "Not overwriting newer docs."
  else
      git push origin gh-pages |& sed s/${GH_TOKEN}/[secure]/g
      echo "Pushed docs to Github Pages"
  fi
fi
