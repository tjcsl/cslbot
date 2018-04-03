#!/bin/bash
p4a apk --sdk-dir=$HOME/android-sdk --ndk-dir=$HOME/crystax-ndk-10.3.2 --android-api=21 --arch=armeabi-v7a --requirements python3crystax \
    --package=edu.tjhsst.cslbot --name "CslBot" --version 0.21 --private .
