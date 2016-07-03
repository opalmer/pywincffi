"""
Test Utility
------------

This module is used by the unittests.
"""

import os
import socket
import subprocess
import sys
from random import choice
from string import ascii_lowercase, ascii_uppercase
from textwrap import dedent

from cffi import FFI, CDefError, FFIError
from mock import patch

try:
    # The setup.py file installs unittest2 for Python 2
    # which backports newer test framework features.
    from unittest2 import TestCase as _TestCase
except ImportError:  # pragma: no cover
    # pylint: disable=wrong-import-order
    from unittest import TestCase as _TestCase

from pywincffi.core import dist
from pywincffi.core.logger import get_logger

logger = get_logger("core.testutil")

# To keep lint on non-windows platforms happy.
try:
    WindowsError
except NameError:  # pragma: no cover
    WindowsError = OSError  # pylint: disable=redefined-builtin


class LibraryWrapper(object):  # pylint: disable=too-few-public-methods
    """
    Used by :meth:`TestCase.mock_library` to replace specific
    attributes on a compiled library.
    """
    def __init__(self, library, attributes):
        self.library = library
        self.attributes = {}

        for attribute, value in attributes.items():
            if not hasattr(library, attribute):
                raise AttributeError(
                    "No such attribute %r on library" % attribute)

            self.attributes[attribute] = value

    def __getattr__(self, item):
        if item in self.attributes:
            return self.attributes[item]

        return getattr(self.library, item)


def mock_library(**attributes):
    """
    Used to replace an attribute the library that :func:`dist.load`
    returns.  Useful for replacing part of the compiled library as part
    of the test.
    """
    ffi, library = dist.load()
    return patch.object(
        dist, "load", lambda: [ffi, LibraryWrapper(library, attributes)])


class TestCase(_TestCase):
    """
    A base class for all test cases.  By default the
    core test case just provides some extra functionality.
    """
    REQUIRES_INTERNET = False
    _HAS_INTERNET = None
    _ffi = None
    _kernel32 = None
    _ws2_32 = None

    def setUp(self):  # pragma: no cover
        if self.REQUIRES_INTERNET and not self.internet_connected():
            if os.environ.get("CI"):
                self.fail(
                    "Test requires internet but we do not seem to be "
                    "connected.")

            self.skipTest("Internet unavailable")

        # Build the small FFI module we need for use in the tests
        if os.name == "nt":
            if self._ffi is None:  # pragma: no cover
                self._ffi = FFI()
                self._ffi.set_unicode(True)
                self._ffi.cdef(dedent("""
                void SetLastError(DWORD);
                void WSASetLastError(int);
                """))

                try:
                    self._kernel32 = self._ffi.dlopen("kernel32")
                    self._ws2_32 = self._ffi.dlopen("ws2_32")
                except (AttributeError, OSError, CDefError, FFIError):
                    self.fail("Failed to build internal _ffi module")

            # Always reset the last error to 0 between tests.  This
            # ensures that any error we intentionally throw in one
            # test does not causes an error to be raised in another.
            self._kernel32.SetLastError(0)
            self._ws2_32.WSASetLastError(0)

    @classmethod
    def internet_connected(cls):
        """
        Returns ``True`` if there appears to be internet access by attempting
        to connect to a few different domains.  The first answer will be
        cached.
        """
        if TestCase._HAS_INTERNET is not None:
            return TestCase._HAS_INTERNET

        original_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(1)

        for hostname in ("github.com", "readthedocs.org", "example.com"):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.connect((hostname, 80))
                TestCase._HAS_INTERNET = True
                break

            # pylint: disable=broad-except
            except Exception:  # pragma: no cover
                pass

            finally:
                sock.close()

        else:  # pragma: no cover
            TestCase._HAS_INTERNET = False

        socket.setdefaulttimeout(original_timeout)
        return TestCase._HAS_INTERNET

    def _terminate_process(self, process):  # pylint: disable=no-self-use
        """
        Calls terminnate() on ``process`` and ignores any errors produced.
        """
        try:
            process.terminate()

        # pylint: disable=broad-except
        except Exception:  # pragma: no cover
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
