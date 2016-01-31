"""
Test Utility
------------

This module is used by the unittests.
"""

import os
import subprocess
import sys
from random import choice
from string import ascii_lowercase, ascii_uppercase

from cffi import FFI, CDefError

try:
    # The setup.py file installs unittest2 for Python 2
    # which backports newer test framework features.
    from unittest2 import TestCase as _TestCase
except ImportError:  # pragma: no cover
    # pylint: disable=wrong-import-order
    from unittest import TestCase as _TestCase

from pywincffi.core.config import config
from pywincffi.core.logger import get_logger

logger = get_logger("core.testutil")

# To keep lint on non-windows platforms happy.
try:
    WindowsError
except NameError:  # pragma: no cover
    WindowsError = OSError  # pylint: disable=redefined-builtin

# Load in our own kernel32 with the function(s) we need
# so we don't have to rely on pywincffi.core
libtest = None  # pylint: disable=invalid-name
ffi = FFI()

try:
    ffi.cdef("void SetLastError(DWORD);")
    libtest = ffi.dlopen("kernel32")  # pylint: disable=invalid-name
except (AttributeError, OSError, CDefError):  # pragma: no cover
    if os.name == "nt":
        logger.warning("Failed to build SetLastError()")


class TestCase(_TestCase):
    """
    A base class for all test cases.  By default the
    core test case just provides some extra functionality.
    """
    def setUp(self):
        if os.name == "nt":  # pragma: no cover
            # Always reset the last error to 0 between tests.  This
            # ensures that any error we intentionally throw in one
            # test does not causes an error to be raised in another.
            self.SetLastError(0)

        config.load()

    # pylint: disable=invalid-name
    def SetLastError(self, value=0, lib=None):  # pragma: no cover
        """Calls the Windows API function SetLastError()"""
        if os.name != "nt":
            self.fail("Only an NT system should call this method")

        if lib is None:
            lib = libtest

        if lib is None:
            self.fail("`lib` was not defined")

        if not isinstance(value, int):
            self.fail("Expected int for `value`")

        return lib.SetLastError(ffi.cast("DWORD", value))

    def _terminate_process(self, process):  # pylint: disable=no-self-use
        """
        Calls terminnate() on ``process`` and ignores any errors produced.
        """
        try:
            process.terminate()
        except Exception:  # pylint: disable=broad-except
            pass

    def create_python_process(self, command):
        """Creates a Python process that run ``command``"""
        process = subprocess.Popen(
            [sys.executable, "-c", command],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(self._terminate_process, process)
        return process

    def random_string(self, length):
        """
        Returns a random string as long as ``length``.  The first character
        will always be a letter.  All other characters will be A-F,
        A-F or 0-9.
        """
        if length < 1:  # pragma: no cover
            self.fail("Length must be at least 1.")

        # First character should always be a letter so the string
        # can be used in object names.
        output = choice(ascii_lowercase)
        length -= 1

        while length:
            length -= 1
            output += choice(ascii_lowercase + ascii_uppercase + "0123456789")

        return output
