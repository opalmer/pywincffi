import os

from pywincffi.core import dist
from pywincffi.dev.testutil import TestCase
from pywincffi.exceptions import WindowsAPIError
from pywincffi.kernel32.io import CloseHandle
from pywincffi.kernel32.process import OpenProcess


class TestOpenProcess(TestCase):
    """
    Tests for :func:`pywincffi.kernel32.OpenProcess`
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

    def test_handle_is_valid(self):
        ffi, library = dist.load()
        handle = OpenProcess(
            library.PROCESS_QUERY_INFORMATION, False, os.getpid())

        # If the handle were invalid, this would fail.
        CloseHandle(handle)
