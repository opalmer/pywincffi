"""
Lint Utilities
==============

Plugins and utilities for lint checks.
"""

import re
from functools import partial
from os.path import dirname, abspath, join

from astroid import MANAGER, scoped_nodes

HEADERS_DIR = join(
    dirname(dirname(abspath(__file__))), "core", "cdefs", "headers")
CONSTANTS_HEADER = join(HEADERS_DIR, "constants.h")
FUNCTIONS_HEADER = join(HEADERS_DIR, "functions.h")

REGEX_FUNCTION = re.compile("^[A-Z]+ ([A-Z][a-z]*[A-Z].*)\(.*$")
REGEX_CONSTANT = re.compile("^#define ([A-Z_])+ ...$")


def transform(cls, constants=None, functions=None):
    """
    Transforms class objects from pylint so they're aware of extra
    attributes that are not present when being statically analyzed.
    """
    assert isinstance(constants, set)
    assert isinstance(functions, set)

    # TODO: needs to change once we FFILibrary returns the prebuilt lib
    if cls.name == "FFILibrary":
        for value in constants:
            cls.locals[value] = [scoped_nodes.Class(value, None)]

        for value in functions:
            cls.locals[value] = [scoped_nodes.Function(value, None)]


def register(linter):
    """
    An entrypoint that pylint uses to search for and register
    plugins with the given ``linter``
    """
    # Load constants
    constants = set()
    with open(CONSTANTS_HEADER, "r") as constants_file:
        for line in constants_file:
            match = REGEX_CONSTANT.match(line)
            if match:
                constants.add(match.group(1))

    # Load functions
    functions = set()
    with open(FUNCTIONS_HEADER, "r") as functions_file:
        for line in functions_file:
            match = REGEX_FUNCTION.match(line)
            if match:
                functions.add(match.group(1))

    MANAGER.register_transform(
        scoped_nodes.Class,
        partial(transform, constants=constants, functions=functions))
