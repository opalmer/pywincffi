import os
import ctypes
import tempfile
import subprocess
import sys
from errno import EEXIST
from os.path import isfile

from mock import patch
from six import text_type

from pywincffi.core import dist
from pywincffi.dev.testutil import TestCase
from pywincffi.exceptions import WindowsAPIError, InputError
from pywincffi.kernel32 import file as _file  # used for mocks
from pywincffi.kernel32 import (
    CreateFile, CloseHandle, MoveFileEx, WriteFile, FlushFileBuffers,
    LockFileEx, UnlockFileEx, ReadFile, GetTempPath)
from pywincffi.wintypes import handle_from_file


class TestWriteFile(TestCase):
    """
    Tests for :func:`pywincffi.kernel32.WriteFile`
    """
    def create_handle(self):
        fd, path = tempfile.mkstemp()
        self.addCleanup(os.remove, path)
        file_ = os.fdopen(fd, "w")
        self.addCleanup(file_.close)
        handle = handle_from_file(file_)
        return handle, path

    def test_write_binary(self):
        handle, path = self.create_handle()
        WriteFile(handle, b"hello world")
        FlushFileBuffers(handle)
        with open(path, "rb") as file_:
            self.assertEqual(file_.read(), b"hello world")

    def test_write_binary_num_bytes(self):
        handle, path = self.create_handle()
        WriteFile(handle, b"hello world", nNumberOfBytesToWrite=5)
        FlushFileBuffers(handle)
        with open(path, "rb") as file_:
            self.assertEqual(file_.read(), b"hello")


class TestReadFile(TestCase):
    """
    Tests for :func:`pywincffi.kernel32.ReadFile`
    """
    def _create_file(self, contents):
        fd, path = tempfile.mkstemp()
        self.addCleanup(os.remove, path)
        with os.fdopen(fd, "wb") as file_:
            file_.write(contents)
        return text_type(path), len(contents)

    def _handle_to_read_file(self, path):
        _, library = dist.load()
        # OPEN_EXISTING prevents the file from being truncated.
        hFile = CreateFile(
            path,
            dwDesiredAccess=library.GENERIC_READ,
            dwCreationDisposition=library.OPEN_EXISTING,
        )
        self.addCleanup(CloseHandle, hFile)
        return hFile

    def test_lpBuffer_smaller_than_nNumberOfBytesToRead(self):
        path, _ = self._create_file(b"")
        hFile = self._handle_to_read_file(path)

        with self.assertRaisesRegex(
            InputError, r".*The length of `lpBuffer` is.*"
        ):
            ReadFile(hFile, bytearray(0), 1)

    def test_lpBuffer_equal_to_nNumberOfBytesToRead(self):
        path, _ = self._create_file(b"")
        hFile = self._handle_to_read_file(path)
        ReadFile(hFile, bytearray(1), 1)  # Should not raise exception

    def test_read(self):
        path, written = self._create_file(b"hello world")
        self.assertEqual(written, 11)
        hFile = self._handle_to_read_file(path)
        lpBuffer = bytearray(written)
        read = ReadFile(hFile, lpBuffer, 5)
        self.assertEqual(read, 5)
        self.assertEqual(lpBuffer[:read], bytearray(b"hello"))

        # The rest of the buffer is essentially unmanaged but let's be sure
        # the remainder of the buffer has not been modified by ReadFile().
        self.assertEqual(
            lpBuffer[read:], bytearray(b"\x00\x00\x00\x00\x00\x00"))


class TestMoveFileEx(TestCase):
    """
    Tests for :func:`pywincffi.kernel32.MoveFileEx`
    """
    def test_replaces_file(self):
        # Destination file exists, this should replace it.
        file_contents = self.random_string(12)
        fd, path1 = tempfile.mkstemp()

        with os.fdopen(fd, "w") as file_:
            file_.write(file_contents)

        fd, path2 = tempfile.mkstemp()
        self.addCleanup(os.remove, path2)
        os.close(fd)

        path1 = text_type(path1)
        path2 = text_type(path2)
        MoveFileEx(path1, path2)

        with open(path2, "r") as file_:
            self.assertEqual(file_.read(), file_contents)

        self.assertFalse(isfile(path1))

    def _remove_file(self, path):
        try:
            os.remove(path)
        except OSError:
            pass

    def test_renames_file(self):
        # Destination file does not exist, this should create it.
        file_contents = self.random_string(12)
        fd, path1 = tempfile.mkstemp()
        path2 = path1 + ".new"
        self.addCleanup(self._remove_file, path1)
        self.addCleanup(self._remove_file, path2)

        with os.fdopen(fd, "w") as file_:
            file_.write(file_contents)

        path1 = text_type(path1)
        path2 = text_type(path2)
        MoveFileEx(path1, path2)

        with open(path2, "r") as file_:
            self.assertEqual(file_.read(), file_contents)

        self.assertFalse(isfile(path1))

    def test_run_delete_after_reboot(self):
        fd, path = tempfile.mkstemp('-removed-on-next-reboot')
        os.close(fd)

        path = text_type(path)

        _, library = dist.load()
        try:
            MoveFileEx(path, None, dwFlags=library.MOVEFILE_DELAY_UNTIL_REBOOT)
        except WindowsAPIError as error:
            # If we're not an administrator then we don't
            # have the permissions to perform this kind of
            # action.
            if error.errno == library.ERROR_ACCESS_DENIED:
                self.SetLastError(0)
                self.addCleanup(os.remove, path)
                self.assertFalse(ctypes.windll.shell32.IsUserAnAdmin())
                return

            raise
        else:
            self.assertTrue(isfile(path))


class TestCreateFile(TestCase):
    """
    Tests for :func:`pywincffi.kernel32.CreateFile`
    """
    def test_creates_file(self):
        fd, path = tempfile.mkstemp()
        os.close(fd)
        os.remove(path)

        path = text_type(path)
        handle = CreateFile(path, 0)
        self.addCleanup(os.remove, path)
        self.addCleanup(CloseHandle, handle)
        self.assertTrue(isfile(path))

    def test_default_create_disposition(self):
        # The default creation disposition should
        # overwrite an existing file.
        fd, path = tempfile.mkstemp()
        with os.fdopen(fd, "w") as file_:
            file_.write("Hello, world.")
            file_.flush()
            os.fsync(file_.fileno())

        path = text_type(path)
        handle = CreateFile(path, 0)
        self.addCleanup(os.remove, path)
        self.addCleanup(CloseHandle, handle)

        _, library = dist.load()
        self.assert_last_error(library.ERROR_ALREADY_EXISTS)

        with open(path, "r") as file_:
            self.assertEqual(file_.read(), "")

    def test_ignores_error_already_existed(self):
        _, library = dist.load()
        fd, path = tempfile.mkstemp()
        os.close(fd)
        os.remove(path)

        def raise_(*_):
            raise WindowsAPIError("", "", library.ERROR_ALREADY_EXISTS)

        with patch.object(_file, "error_check", side_effect=raise_):
            path = text_type(path)
            handle = CreateFile(
                path, 0, dwCreationDisposition=library.CREATE_ALWAYS)
            self.addCleanup(os.remove, path)
            self.addCleanup(CloseHandle, handle)

        # If we've made it this far, the exception was ignored by CreateFile

    def test_raises_other_errors_for_create_always(self):
        _, library = dist.load()

        with self.assertRaises(WindowsAPIError) as error:
            handle = CreateFile(
                u"", 0, dwCreationDisposition=library.CREATE_ALWAYS)
            self.addCleanup(CloseHandle, handle)

        self.assert_last_error(library.ERROR_PATH_NOT_FOUND)
        self.assertEqual(error.exception.errno, library.ERROR_PATH_NOT_FOUND)


class LockFileCase(TestCase):
    def setUp(self):
        super(LockFileCase, self).setUp()
        fd, path = tempfile.mkstemp()
        self.path = path
        os.close(fd)
        self.addCleanup(os.remove, path)
        _, library = dist.load()
        path = text_type(path)
        self.handle = CreateFile(path, library.GENERIC_WRITE)
        self.assert_last_error(library.ERROR_ALREADY_EXISTS)
        self.addCleanup(CloseHandle, self.handle)

        WriteFile(self.handle, b"hello")


class TestLockFileEx(LockFileCase):
    """
    Tests for :func:`pywincffi.kernel32.LockFileEx`
    """
    def test_lock_causes_subprocess_read_failure(self):
        _, library = dist.load()
        LockFileEx(
            self.handle,
            library.LOCKFILE_EXCLUSIVE_LOCK |
            library.LOCKFILE_FAIL_IMMEDIATELY,
            0, 1024)

        with self.assertRaises(subprocess.CalledProcessError):
            subprocess.check_call(
                [sys.executable, "-c", "open(%r, 'r').read()" % self.path],
                stderr=subprocess.PIPE
            )

    def test_no_lock_allows_subprocess_read_python3(self):
        # This makes sure that if the default behavior changes or varies
        # between Python versions we catch it.  Without this there's not a way
        # to ensure that test_lock_causes_subprocess_read_failure() is really
        # testing the behavior of LockFileEx()
        subprocess.check_call(
            [sys.executable, "-c", "open(%r, 'r').read()" % self.path],
            stderr=subprocess.PIPE
        )


class TestUnlockFileEx(LockFileCase):
    """
    Tests for :func:`pywincffi.kernel32.UnlockFileEx`
    """
    def test_unlock_file(self):
        _, library = dist.load()
        LockFileEx(
            self.handle,
            library.LOCKFILE_EXCLUSIVE_LOCK |
            library.LOCKFILE_FAIL_IMMEDIATELY,
            0, 1024)

        with self.assertRaises(subprocess.CalledProcessError):
            subprocess.check_call(
                [sys.executable, "-c", "open(%r, 'r').read()" % self.path],
                stderr=subprocess.PIPE
            )

        UnlockFileEx(self.handle, 0, 1024)

        subprocess.check_call([
            sys.executable, "-c", "open(%r, 'r').read()" % self.path])


class TestGetTempPath(TestCase):
    def test_call(self):
        path = GetTempPath()
        try:
            os.makedirs(path)
        except OSError as err:
            self.assertEqual(err.errno, EEXIST)
