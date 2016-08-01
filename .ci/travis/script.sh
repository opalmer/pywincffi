#!/bin/bash -e

if [[ $READTHEDOCS == "1" ]]; then
    make -C docs html
    make -C docs linkcheck
fi

