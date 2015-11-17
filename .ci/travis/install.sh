#!/bin/bash -e

# Required for building docs and static analysis.
pip install unittest2

if [[ $PYLINT == "1" ]] && [[ $TRAVIS_PYTHON_VERSION == "2.6" ]]; then
    pip install pylint<1.4 pep8

elif [[ $PYLINT == "1" ]]; then
    pip install pylint pep8

fi

if [[ $READTHEDOCS == "1" ]]; then
    pip install sphinx
fi

pip install .
