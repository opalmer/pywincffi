import os

from pywincffi.core.ffi import Library
from pywincffi.core.testutil import TestCase
from pywincffi.exceptions import WindowsAPIError
from pywincffi.kernel32.process import OpenProcess


class TestOpenProcess(TestCase):
    """
    Tests for :func:`pywincffi.kernel32.OpenProcess`
    """
    def test_returns_handle(self):
        ffi, library = Library.load()

        handle = OpenProcess(
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
