#!/usr/bin/env bash

if [[ $PYLINT == "1" ]]; then
    retry pip install pylint
fi
