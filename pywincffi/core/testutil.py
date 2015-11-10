"""
Test Utility
------------

This module is used by the unittests.
"""

import atexit
import os
import shutil
import sys
from errno import ENOENT
from os.path import isfile, isdir

from cffi import FFI

if sys.version_info[0:2] == (2, 6):
    from unittest2 import TestCase as _TestCase
else:
    from unittest import TestCase as _TestCase

# Load in our own kernel32 with the function(s) we need
# so we don't have to rely on pywincffi.core
kernel32 = None
if not os.environ.get("READTHEDOCS"):
    ffi = FFI()
    ffi.cdef("void SetLastError(DWORD);")
    kernel32 = ffi.dlopen("kernel32")


class TestCase(_TestCase):
    """
    A base class for all test cases.  By default the
    core test case just provides some extra functionality.
    """
    def setUp(self):
        self.failIf(kernel32 is None, "kernel32 was never defined")

        # Always reset the last error to 0 between tests.  This
        # ensures that any error we intentionally throw in one
        # test does not causes an error to be raised in another.
        kernel32.SetLastError(ffi.cast("DWORD", 0))

    def remove(self, path, onexit=True):
        """
        Single function to remove a file or directory.  If there are
        problems while attempting to remove the path we'll try again
        when the tests exit.
        """
        if isfile(path):
            remove = os.remove
        elif isdir(path):
            remove = shutil.rmtree
        else:
            return

        try:
            remove(path)
        except (OSError, IOError, WindowsError) as e:
            if e.errno != ENOENT and onexit:
                atexit.register(self.remove, path, onexit=False)

