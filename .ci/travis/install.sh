#!/bin/bash -e

if [[ $PYLINT == "1" ]]; then
    pip install pylint pep8
fi

if [[ $READTHEDOCS == "1" ]]; then
    pip install sphinx
fi

pip install .
