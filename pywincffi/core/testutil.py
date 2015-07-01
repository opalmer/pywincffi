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

try:
    WindowsError
except NameError:  # pragma: no cover
    WindowsError = OSError

if sys.version_info[0:2] == (2, 6):
    from unittest2 import TestCase as _TestCase
else:
    from unittest import TestCase as _TestCase


class TestCase(_TestCase):
    """
    A base class for all test cases.  By default the
    core test case just provides some extra functionality.
    """
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
