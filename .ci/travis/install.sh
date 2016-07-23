#!/bin/bash -e

# Required for building docs and static analysis.
pip install .
pip install -r dev_requirements.txt --upgrade
