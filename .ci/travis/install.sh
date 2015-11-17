#!/bin/bash -e

# Required for building docs and static analysis.
pip install unittest2 pep8 sphinx

if [[ $TRAVIS_PYTHON_VERSION == "2.6" ]]; then
    pip install pylint<1.4
else
    pip install pylint
fi

pip install .
