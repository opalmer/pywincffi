from pywincffi.core import dist
from pywincffi.dev.testutil import TestCase
from pywincffi.kernel32.error import (
    GetLastError, SetLastError, get_error_message)


class TestError(TestCase):
    # These test cases will manipulate the current error code. Because
    # this behavior is expected we don't want to run this function.
    def unhandled_error_check(self):
        pass

    def test_get_last_error(self):
        self.assertEqual(GetLastError(), 0)

    def test_get_last_error_after_set(self):
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
