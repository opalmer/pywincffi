import os
import shutil
import socket
import subprocess
import sys
import tempfile
from errno import EBADF

from pywincffi.core import dist
from pywincffi.dev.testutil import TestCase
from pywincffi.exceptions import InputError, WindowsAPIError
from pywincffi.kernel32 import (
    GetStdHandle, CloseHandle, OpenProcess, WaitForSingleObject,
    handle_from_file, GetHandleInformation, SetHandleInformation)

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
        fd, path = tempfile.mkstemp()
        self.addCleanup(os.unlink, path)
        test_file = os.fdopen(fd, "r")
        test_file.close()

        with self.assertRaises(InputError):
            handle_from_file(test_file)

    def test_opens_correct_file_handle(self):
        fd, path = tempfile.mkstemp()
        self.addCleanup(os.unlink, path)
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
    def test_get_handle_info_stdin(self):
        _, library = dist.load()
        stdin_handle = GetStdHandle(library.STD_INPUT_HANDLE)
        handle_flags = GetHandleInformation(stdin_handle)
        inherit = handle_flags & library.HANDLE_FLAG_INHERIT
        expected = (0, library.HANDLE_FLAG_INHERIT)
        self.assertIn(inherit, expected)

    def _expected_inheritance(self):
        # Python >= 3.4 creates non-inheritable handles (PEP 0446)
        _, library = dist.load()
        inherit = library.HANDLE_FLAG_INHERIT
        return inherit if sys.version_info[:2] < (3, 4) else 0

    def test_get_handle_info_file(self):
        _, library = dist.load()
        # can't use mkstemp: not inheritable on Python < 3.4
        tempdir = tempfile.mkdtemp()
        self.addCleanup(os.rmdir, tempdir)
        filename = os.path.join(tempdir, "test_file")
        with open(filename, "w") as test_file:
            self.addCleanup(os.unlink, filename)
            test_file.write("data")
            file_handle = handle_from_file(test_file)
            handle_flags = GetHandleInformation(file_handle)
            inherit = handle_flags & library.HANDLE_FLAG_INHERIT
        expected = self._expected_inheritance()
        self.assertEqual(inherit, expected)

    def test_get_handle_info_socket(self):
        ffi, library = dist.load()
        sock = socket.socket()
        self.addCleanup(sock.close)
        sock_handle = ffi.cast("void *", sock.fileno())
        handle_flags = GetHandleInformation(sock_handle)
        inherit = handle_flags & library.HANDLE_FLAG_INHERIT
        expected = self._expected_inheritance()
        self.assertEqual(inherit, expected)


class TestSetHandleInformation(TestCase):
    """
    Tests for :func:`pywincffi.kernel32.SetHandleInformation`
    """
    def _set_handle_info_file(self, inherit, check=False):
        _, library = dist.load()
        tempdir = tempfile.mkdtemp()
        self.addCleanup(os.rmdir, tempdir)
        filename = os.path.join(tempdir, "test_file")
        with open(filename, "w") as test_file:
            self.addCleanup(os.unlink, filename)
            test_file.write("data")
            file_handle = handle_from_file(test_file)
            SetHandleInformation(
                file_handle,
                library.HANDLE_FLAG_INHERIT,
                inherit
            )
            if check:
                result = GetHandleInformation(file_handle)
                self.assertEqual(inherit, result)

    def test_set_handle_info_file_noinherit(self):
        self._set_handle_info_file(0)

    def test_set_handle_info_file_inherit(self):
        self._set_handle_info_file(1)

    def test_set_get_handle_info_file_noinherit(self):
        self._set_handle_info_file(0, check=True)

    def test_set_get_handle_info_file_inherit(self):
        self._set_handle_info_file(1, check=True)

    def _set_handle_info_socket(self, inherit, check=False):
        ffi, library = dist.load()
        sock = socket.socket()
        self.addCleanup(sock.close)
        sock_handle = ffi.cast("void *", sock.fileno())
        SetHandleInformation(
            sock_handle,
            library.HANDLE_FLAG_INHERIT,
            inherit
        )
        if check:
            result = GetHandleInformation(sock_handle)
            self.assertEqual(inherit, result)

    def test_set_handle_info_socket_noinherit(self):
        self._set_handle_info_socket(0)

    def test_set_handle_info_socket_inherit(self):
        self._set_handle_info_socket(1)

    def test_set_get_handle_info_socket_noinherit(self):
        self._set_handle_info_socket(0, check=True)

    def test_set_get_handle_info_socket_inherit(self):
        self._set_handle_info_socket(1, check=True)


class TestSetHandleInformationChildSpawns(TestCase):
    """
    Integration tests for :func:`pywincffi.kernel32.SetHandleInformation`
    """
    def _spawn_child(self):
        return subprocess.Popen(
            args=[sys.executable],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    def _cleanup_child(self, child):
        child.stdin.close()
        child.wait()

    def test_file_rename_after_spawn(self):
        _, library = dist.load()
        tempdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tempdir, ignore_errors=True)
        filename = os.path.join(tempdir, "original_name")
        with open(filename, "w") as test_file:
            test_file.write("data")
            file_handle = handle_from_file(test_file)
            # prevent file_handle inheritance
            SetHandleInformation(file_handle, library.HANDLE_FLAG_INHERIT, 0)
            # spawn child while test_file is open
            child = self._spawn_child()
            self.addCleanup(self._cleanup_child, child)
        newfilename = os.path.join(tempdir, "new_name")
        # works as long as file is closed and not inherited by child
        os.rename(filename, newfilename)

    def test_socket_rebind_after_spawn(self):
        ffi, library = dist.load()
        bind_addr = (('127.0.0.1', 0))
        sock = socket.socket()
        try:
            sock.bind(bind_addr)
            bind_addr = sock.getsockname()
            sock_handle = ffi.cast("void *", sock.fileno())
            # prevent file_handle inheritance
            SetHandleInformation(sock_handle, library.HANDLE_FLAG_INHERIT, 0)
            # spawn child while sock is bound
            child = self._spawn_child()
            self.addCleanup(self._cleanup_child, child)
        finally:
            sock.close()
        sock = socket.socket()
        self.addCleanup(sock.close)
        # re-bind to same address: works if not inherited by child
        sock.bind(bind_addr)
