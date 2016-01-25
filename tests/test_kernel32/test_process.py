import os

from pywincffi.core import dist
from pywincffi.dev.testutil import TestCase
from pywincffi.exceptions import WindowsAPIError
from pywincffi.kernel32.process import OpenProcess, GetCurrentProcess


class TestOpenProcess(TestCase):
    """
    Tests for :func:`pywincffi.kernel32.process.OpenProcess`
    """
    def test_returns_handle(self):
        ffi, library = dist.load()

        handle = OpenProcess(
            # pylint: disable=no-member
            library.PROCESS_QUERY_LIMITED_INFORMATION,
            False,
            os.getpid()
        )

        typeof = ffi.typeof(handle)
        self.assertEqual(typeof.kind, "pointer")
        self.assertEqual(typeof.cname, "void *")

    def test_access_denied_for_null_desired_access(self):
        with self.assertRaises(WindowsAPIError) as error:
            OpenProcess(0, False, os.getpid())

        self.assertEqual(error.exception.code, 5)


class TestGetCurrentProcess(TestCase):
    """
    Tests for :func:`pywincffi.kernel32.process.GetCurrentProcess`
    """
    def test_returns_handle(self):
        ffi, library = dist.load()
        handle = GetCurrentProcess()
        typeof = ffi.typeof(handle)
        self.assertEqual(typeof.kind, "pointer")
        self.assertEqual(typeof.cname, "void *")

    def test_returns_same_handle(self):
        # GetCurrentProcess is somewhat special in that it will
        # always return a handle to the same object.  However, __eq__ is not
        # opaque so the string representation of the two handles
        # should always match since it contains the address of the object
        # in memory.
        self.assertEqual(repr(GetCurrentProcess()), repr(GetCurrentProcess()))
