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

from cffi import FFI
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


class SharedState(object):  # pylint: disable=too-few-public-methods
    """
    Contains some state data which is shared across multiple
    :class:`TestCase` instances.  This is kept outside of the test
    case class itself so it can't be inadvertently modified by a test
    or fixture.
    """
    HAS_INTERNET = None
    ffi = None
    kernel32 = None
    ws2_32 = None


class TestCase(_TestCase):  # pylint: disable=too-many-public-methods
    """
    A base class for all test cases.  By default the
    core test case just provides some extra functionality.
    """
    # A list of hosts and port to check for internet access on.  If we fail
    # to reach any of the hosts in `INTERNET_HOSTS` on `INTERNET_PORT` then
    # `HAS_INTERNET` will be set to False.
    INTERNET_PORT = 80
    INTERNET_HOSTS = ("github.com", "readthedocs.org", "example.com")
    REQUIRES_INTERNET = False
    HAS_INTERNET = None

    # Class level attributes used to access some specific Windows API
    # functions when testing.  This is kept separate from what `dist.load()`
    # produces so problems in the build don't break parts of the base TestCase.
    ffi = None
    kernel32 = None
    ws2_32 = None

    @classmethod
    def setUpClass(cls):
        # Reset everything back to the default values first.
        cls.ffi = None
        cls.kernel32 = None
        cls.ws2_32 = None
        cls.HAS_INTERNET = None

        # First run and this test case requires internet access.  Determine
        # if we have access to the internet then cache the value.
        if cls.REQUIRES_INTERNET and SharedState.HAS_INTERNET is None:
            original_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(1)

            try:
                for hostname in cls.INTERNET_HOSTS:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    try:
                        sock.connect((hostname, cls.INTERNET_PORT))
                        SharedState.HAS_INTERNET = True
                        break

                    # pylint: disable=broad-except
                    except Exception:  # pragma: no cover
                        pass

                    finally:
                        sock.close()
                else:  # pragma: no cover
                    SharedState.HAS_INTERNET = False
            finally:
                socket.setdefaulttimeout(original_timeout)

        if os.name == "nt" and SharedState.ffi is None:
            try:
                ffi = FFI()
                ffi.set_unicode(True)
                ffi.cdef(dedent("""
                // kernel32 functions
                DWORD GetLastError(void);
                void SetLastError(DWORD);

                // ws2_32 functions
                void WSASetLastError(int);
                int WSAGetLastError(void);
                """))
                SharedState.ffi = ffi
                SharedState.kernel32 = ffi.dlopen("kernel32")
                SharedState.ws2_32 = ffi.dlopen("ws2_32")

            # pylint: disable=broad-except
            except Exception as error:  # pragma: no cover
                if os.name == "nt":
                    # pylint: disable=redefined-variable-type
                    SharedState.ffi = error

        cls.HAS_INTERNET = SharedState.HAS_INTERNET
        cls.ffi = SharedState.ffi
        cls.kernel32 = SharedState.kernel32
        cls.ws2_32 = SharedState.ws2_32

    def setUp(self):  # pragma: no cover
        if self.REQUIRES_INTERNET and not self.HAS_INTERNET:
            if os.environ.get("CI"):
                self.fail(
                    "%s requires internet but we do not seem to be "
                    "connected." % self.__class__.__name__)

            self.skipTest("Internet unavailable")

        if os.name != "nt":
            return

        if isinstance(self.ffi, Exception):
            self.fail("FFI module setup failed: %s" % self.ffi)

        self.assertIsNotNone(
            self.kernel32, "setUp() failed: missing kernel32")
        self.assertIsNotNone(
            self.ws2_32, "setUp() failed: missing ws2_32")

        self.addCleanup(self.unhandled_error_check)

        # Always reset the last error to 0 between tests.  This ensures
        # that if an unhandled API error occurs it won't impact the
        # currently running test.  The cleanup step above will ensure that
        # tests that do not exit cleanly will cause a failure.
        self.kernel32.SetLastError(0)
        self.ws2_32.WSASetLastError(0)

    def GetLastError(self):  # pylint: disable=invalid-name
        """
        Returns a tuple containing output from the Windows GetLastError
        function and the associated error message.  The error message will
        be None if GetLastError() returns 0.
        """
        errno = self.kernel32.GetLastError()
        return errno, self.ffi.getwinerror(errno) if errno != 0 else None

    def WSAGetLastError(self):  # pylint: disable=invalid-name
        """
        Returns a tuple containing output from the Windows WSAGetLastError
        function and the associated error message.  The error message will
        be None if WSAGetLastError() returns 0.
        """
        errno = self.ws2_32.WSAGetLastError()
        return errno, self.ffi.getwinerror(errno) if errno != 0 else None

    def WSASetLastError(self, errno):  # pylint: disable=invalid-name
        """Wrapper for WSASetLastError()"""
        self.ws2_32.WSASetLastError(errno)

    def SetLastError(self, errno):  # pylint: disable=invalid-name
        """Wrapper for SetLastError()"""
        self.kernel32.SetLastError(errno)

    def unhandled_error_check(self):
        """
        A cleanup step which ensures that there are not any uncaught API
        errors left over.  Unhandled errors could be a sign of an unhandled
        testing artifact, improper API usage or other problem.  In any case,
        unhandled errors are often a source of test flake.
        """
        # Check for kernel32 errors.
        k32_errno, k32_message = self.GetLastError()
        self.assertEqual(
            k32_errno, 0,
            msg="Unhandled kernel32 error. Errno: %r. Message: %r" % (
                k32_errno, k32_message))

        # Check for ws2_32 errors.
        ws2_errno, ws2_message = self.WSAGetLastError()
        self.assertEqual(
            ws2_errno, 0,
            msg="Unhandled ws2_32 error. Errno: %r. Message: %r" % (
                ws2_errno, ws2_message))

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
