#!/bin/bash

set -e
set -x

ci_requirements="tox virtualenv"

if [ "$TRAVIS_OS_NAME" == "osx" ]; then
    curl -O https://bootstrap.pypa.io/get-pip.py
    python get-pip.py --user
fi

pip install $ci_requirements
