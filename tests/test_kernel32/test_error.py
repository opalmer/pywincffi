from pywincffi.core import dist
from pywincffi.dev.testutil import TestCase
from pywincffi.exceptions import WindowsAPIError
from pywincffi.kernel32.error import (
    GetLastError, SetLastError, get_error_message, overlapped_error_check)


class Case(TestCase):
    # These test cases will manipulate the current error code. Because
    # this behavior is expected we don't want to run this function.
    def unhandled_error_check(self):
        pass


class TestGetError(Case):
    def test_default_get_last_error(self):
        self.assertEqual(GetLastError(), 0)

    def test_value(self):
        try:
            value = long(4242)
        except NameError:
            value = 4242

        SetLastError(value)
        self.assertEqual(GetLastError(), value)

    def test_get_error_message_no_code_provided(self):
        _, library = dist.load()
        SetLastError(library.ERROR_IO_PENDING)
        self.assertEqual(
            get_error_message(),
            "Overlapped I/O operation is in progress")

    def test_get_error_message_code_provided(self):
        _, library = dist.load()
        self.assertEqual(
            get_error_message(library.ERROR_ACCESS_DENIED),
            "Access is denied")


class TestOverlappedErrorCheck(Case):
    def test_non_overlapped_fail(self):
        with self.assertRaisesRegex(WindowsAPIError, ".+Expected.+0.+"):
            overlapped_error_check("test", 0, None)

    def test_non_overlapped_pass(self):
        overlapped_error_check("test", 50, None)

    def test_overlapped_pass(self):
        _, library = dist.load()
        SetLastError(library.ERROR_IO_PENDING)
        overlapped_error_check("test", 0, {})

    def test_overlapped_fail(self):
        _, library = dist.load()
        SetLastError(library.ERROR_IO_PENDING)
        with self.assertRaisesRegex(WindowsAPIError, ".+Expected.+rece.+50.+"):
            overlapped_error_check("test", 50, {})
