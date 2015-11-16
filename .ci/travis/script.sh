#!/bin/bash -e

if [[ $PYLINT == "1" ]]; then
    pep8 pywincffi
    pylint pywincffi
fi

if [[ $READTHEDOCS == "1" ]]; then
    make -C docs html
    make -C docs linkcheck
fi

