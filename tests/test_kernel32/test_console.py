from pywincffi.core import dist
from pywincffi.dev.testutil import TestCase
from pywincffi.exceptions import InputError, WindowsAPIError
from pywincffi.kernel32 import (
    SetConsoleTextAttribute, CreateConsoleScreenBuffer,
    GetConsoleScreenBufferInfo, CloseHandle, )


class TestSetConsoleTextAttribute(TestCase):
    def test_set(self):
        _, library = dist.load()
        handle = CreateConsoleScreenBuffer(
            library.GENERIC_READ | library.GENERIC_WRITE,
            None, lpSecurityAttributes=None, dwFlags=None,
        )
        self.addCleanup(CloseHandle, handle)

        # Set the console attributes
        wAttributes = library.FOREGROUND_RED | library.BACKGROUND_INTENSITY
        SetConsoleTextAttribute(handle, wAttributes)

        # Query the results
        info = GetConsoleScreenBufferInfo(handle)
        self.assertEqual(info.wAttributes, wAttributes)


class TestGetConsoleScreenBufferInfo(TestCase):
    def test_access_denied(self):
        _, library = dist.load()
        handle = CreateConsoleScreenBuffer(
            library.GENERIC_WRITE,
            None, lpSecurityAttributes=None, dwFlags=None,
        )
        self.addCleanup(CloseHandle, handle)

        # We should get ERROR_ACCESS_DENIED here because we didn't
        # include the GENERIC_READ permission in the call to
        # CreateConsoleScreenBuffer above.
        try:
            GetConsoleScreenBufferInfo(handle)
        except WindowsAPIError as err:
            self.addCleanup(self.SetLastError, 0)
            self.assertEqual(err.errno, library.ERROR_ACCESS_DENIED)


class TestCreateConsoleScreenBuffer(TestCase):
    def test_dwDesiredAccess_input(self):
        match = r".*Value of 'dwDesiredAccess' is 4242.*"
        with self.assertRaisesRegex(InputError, match):
            CreateConsoleScreenBuffer(4242, None, None, None)

    def test_create_console(self):
        _, library = dist.load()
        handle = CreateConsoleScreenBuffer(
            library.GENERIC_READ | library.GENERIC_WRITE,
            None, lpSecurityAttributes=None, dwFlags=None,
        )
        self.addCleanup(CloseHandle, handle)
