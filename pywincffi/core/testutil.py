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

import six

if sys.version_info[0:2] == (2, 6):
    from unittest2 import TestCase as _TestCase
else:
    from unittest import TestCase as _TestCase

from pywincffi.core.ffi import ffi, bind


kernel32 = bind(ffi, "kernel32")


class TestCase(_TestCase):
    """
    A base class for all test cases.  By default the
    core test case just provides some extra functionality.
    """
    def setUp(self):
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
