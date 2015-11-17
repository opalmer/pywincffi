#!/bin/bash -e

# Required for building docs and static analysis.
pip install unittest2 pep8 sphinx pylint
pip install .
