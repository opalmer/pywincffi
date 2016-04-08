import sys
import os
import tempfile
import socket
from errno import EBADF

from pywincffi.core import dist
from pywincffi.dev.testutil import TestCase
from pywincffi.exceptions import InputError, WindowsAPIError
from pywincffi.kernel32 import (
    GetStdHandle, CloseHandle, OpenProcess, WaitForSingleObject,
    handle_from_file, GetHandleInformation)

try:
    WindowsError
except NameError:  # pragma: no cover
    WindowsError = OSError  # pylint: disable=redefined-builtin


class TestGetStdHandle(TestCase):
    """
    Tests for :func:`pywincffi.kernel32.GetStdHandle`
    """
    def test_stdin_handle(self):
        _, library = dist.load()
        self.assertEqual(
            GetStdHandle(library.STD_INPUT_HANDLE),
            library.GetStdHandle(library.STD_INPUT_HANDLE)
        )

    def test_stdout_handle(self):
        _, library = dist.load()
        self.assertEqual(
            GetStdHandle(library.STD_OUTPUT_HANDLE),
            library.GetStdHandle(library.STD_OUTPUT_HANDLE)
        )

    def test_stderr_handle(self):
        _, library = dist.load()
        self.assertEqual(
            GetStdHandle(library.STD_ERROR_HANDLE),
            library.GetStdHandle(library.STD_ERROR_HANDLE)
        )


class TestGetHandleFromFile(TestCase):
    """
    Tests for :func:`pywincffi.kernel32.handle_from_file`
    """
    def test_fails_if_not_a_file(self):
        with self.assertRaises(InputError):
            handle_from_file(0)

    def test_fails_if_file_is_not_open(self):
        fd, _ = tempfile.mkstemp()
        test_file = os.fdopen(fd, "r")
        test_file.close()

        with self.assertRaises(InputError):
            handle_from_file(test_file)

    def test_opens_correct_file_handle(self):
        fd, path = tempfile.mkstemp()
        os.close(fd)

        test_file = open(path, "w")
        handle = handle_from_file(test_file)

        CloseHandle(handle)

        # If CloseHandle() was passed the same handle
        # that test_file is trying to write to the file
        # and/or flushing it should fail.
        try:
            test_file.write("foo")
            test_file.flush()
        except (OSError, IOError, WindowsError) as error:
            # EBADF == Bad file descriptor (because CloseHandle closed it)
            self.assertEqual(error.errno, EBADF)
        else:
            self.fail("Expected os.close(%r) to fail" % fd)


class TestWaitForSingleObject(TestCase):
    """
    Tests for :func:`pywincffi.kernel32.WaitForSingleObject`
    """
    def test_wait_failed(self):
        # This should cause WAIT_FAILED to be returned by the underlying
        # WaitForSingleObject because we didn't request the SYNCHRONIZE
        # permission.
        process = self.create_python_process("import time; time.sleep(3)")
        _, library = dist.load()

        hProcess = OpenProcess(
            library.PROCESS_QUERY_INFORMATION, False, process.pid)
        self.addCleanup(CloseHandle, hProcess)

        with self.assertRaises(WindowsAPIError) as exec_:
            WaitForSingleObject(hProcess, 3)
            self.assertEqual(exec_.code, library.WAIT_FAILED)

    def test_wait_on_running_process(self):
        process = self.create_python_process("import time; time.sleep(1)")
        _, library = dist.load()

        hProcess = OpenProcess(
            library.PROCESS_QUERY_INFORMATION | library.SYNCHRONIZE,
            False, process.pid)
        self.addCleanup(CloseHandle, hProcess)
        self.assertEqual(
            WaitForSingleObject(hProcess, 0), library.WAIT_TIMEOUT)

    def test_process_dies_before_timeout(self):
        process = self.create_python_process("import time; time.sleep(1)")
        _, library = dist.load()

        hProcess = OpenProcess(
            library.PROCESS_QUERY_INFORMATION | library.SYNCHRONIZE,
            False, process.pid)
        self.addCleanup(CloseHandle, hProcess)
        self.assertEqual(
            WaitForSingleObject(hProcess, library.INFINITE),
            library.WAIT_OBJECT_0)


class TestGetHandleInformation(TestCase):
    """
    Tests for :func:`pywincffi.kernel32.GetHandleInformation`
    """
    def _expected_inheritance(self):
        # Python >= 3.4 creates non-inheritable handles (PEP 0446)
        if sys.hexversion >= 0x30400f0:
            return 0
        else:
            return 1

    def test_get_handle_info_stdin(self):
        _, library = dist.load()
        handle_stdin = GetStdHandle(library.STD_INPUT_HANDLE)
        inherit = GetHandleInformation(handle_stdin) & 1
        expected = self._expected_inheritance()
        self.assertEqual(inherit, expected)

    def test_get_handle_info_file(self):
        # can't use mkstemp: not inheritable on Python < 3.4
        dirname = tempfile.mkdtemp()
        filename = os.path.join(dirname, "test_file")
        test_file = open(filename, "w")
        test_file.write("data")
        file_handle = handle_from_file(test_file)
        inherit = GetHandleInformation(file_handle) & 1

        expected = self._expected_inheritance()
        self.assertEqual(inherit, expected)
        test_file.close()
        os.unlink(filename)
        os.rmdir(dirname)


    def test_get_handle_info_socket(self):
        ffi, _ = dist.load()
        s = socket.socket()
        socket_handle = ffi.cast('void *', s.fileno())

        inherit = GetHandleInformation(socket_handle) & 1
        expected = self._expected_inheritance()
        self.assertEqual(inherit, expected)
        s.close()

