#!/bin/bash -e

if [[ $PYLINT == "1" ]]; then
    pep8 pywincffi tests
    pylint pywincffi

    # Run pylint on the tests too but disable some of the
    # more noisy checks that don't effect quality for testing
    # purposes.
    pylint tests \
        --disable missing-docstring,invalid-name \
        --disable protected-access,no-self-use,unused-argument
fi

if [[ $READTHEDOCS == "1" ]]; then
    make -C docs html
    make -C docs linkcheck
fi

