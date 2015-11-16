#!/bin/bash -e

if [[ $PYLINT == "1" ]]; then
    pip install pylint
fi

if [[ $READTHEDOCS == "1" ]]; then
    pip install sphinx
fi
