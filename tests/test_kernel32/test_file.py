import os
import ctypes
import tempfile
import subprocess
import sys
from os.path import isfile

from mock import patch
from six import PY2, PY3

from pywincffi.core import dist
from pywincffi.dev.testutil import TestCase
from pywincffi.exceptions import WindowsAPIError

from pywincffi.kernel32 import file as _file  # used for mocks
from pywincffi.kernel32 import (
    CreateFile, CloseHandle, MoveFileEx, WriteFile, FlushFileBuffers,
    LockFileEx, UnlockFileEx, handle_from_file, ReadFile)


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
        with open(path, "r") as file_:
            self.assertEqual(file_.read(), b"hello world")


class TestReadFile(TestCase):
    """
    Tests for :func:`pywincffi.kernel32.ReadFile`
    """
    def _create_file(self, contents):
        fd, path = tempfile.mkstemp()
        self.addCleanup(os.remove, path)
        with os.fdopen(fd, "w") as file_:
            file_.write(contents)
        return path if PY3 else unicode(path)

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

    def test_write_then_read_bytes_ascii(self):
        path = self._create_file(b"test_write_then_read_bytes_ascii contents")
        hFile = self._handle_to_read_file(path)
        contents = ReadFile(hFile, 1024)
        self.assertEqual(contents, b"test_write_then_read_bytes_ascii contents")

    def test_write_then_read_null_bytes(self):
        path = self._create_file(b"hello\x00world")
        hFile = self._handle_to_read_file(path)
        contents = ReadFile(hFile, 1024)
        self.assertEqual(contents, b"hello\x00world")

    def test_write_then_read_partial(self):
        path = self._create_file(b"test_write_then_read_partial contents")
        hFile = self._handle_to_read_file(path)
        contents = ReadFile(hFile, 4)
        self.assertEqual(contents, b"test")


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

        if PY2:
            path1 = unicode(path1)
            path2 = unicode(path2)
        MoveFileEx(path1, path2)

        with open(path2, "r") as file_:
            self.assertEqual(file_.read(), file_contents)

        self.assertFalse(isfile(path1))

    def test_renames_file(self):
        # Destination file does not exist, this should create it.
        file_contents = self.random_string(12)
        fd, path1 = tempfile.mkstemp()
        path2 = path1 + ".new"

        with os.fdopen(fd, "w") as file_:
            file_.write(file_contents)

        if PY2:
            path1 = unicode(path1)
            path2 = unicode(path2)
        MoveFileEx(path1, path2)

        with open(path2, "r") as file_:
            self.assertEqual(file_.read(), file_contents)

        self.assertFalse(isfile(path1))

    def test_run_delete_after_reboot(self):
        fd, path = tempfile.mkstemp()
        os.close(fd)

        if PY2:
            path = unicode(path)

        _, library = dist.load()
        try:
            MoveFileEx(path, None, dwFlags=library.MOVEFILE_DELAY_UNTIL_REBOOT)
        except WindowsAPIError as error:
            # If we're not an administrator then we don't
            # have the permissions to perform this kind of
            # action.
            if error.errno == library.ERROR_ACCESS_DENIED:
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

        if PY2:
            path = unicode(path)
        handle = CreateFile(path, 0)
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

        if PY2:
            path = unicode(path)
        handle = CreateFile(path, 0)
        self.addCleanup(CloseHandle, handle)

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
            if PY2:
                path = unicode(path)
            handle = CreateFile(
                path, 0, dwCreationDisposition=library.CREATE_ALWAYS)
            self.addCleanup(CloseHandle, handle)

        # If we've made it this far, the exception was ignored by CreateFile

    def test_raises_other_errors_for_create_always(self):
        _, library = dist.load()

        with self.assertRaises(WindowsAPIError) as error:
            handle = CreateFile(
                u"", 0, dwCreationDisposition=library.CREATE_ALWAYS)
            self.addCleanup(CloseHandle, handle)

        self.assertEqual(error.exception.errno, library.ERROR_PATH_NOT_FOUND)


class LockFileCase(TestCase):
    def setUp(self):
        super(LockFileCase, self).setUp()
        fd, path = tempfile.mkstemp()
        self.path = path
        os.close(fd)
        self.addCleanup(os.remove, path)
        _, library = dist.load()
        if PY2:
            path = unicode(path)
        self.handle = CreateFile(path, library.GENERIC_WRITE)
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
            subprocess.check_call([
                sys.executable, "-c", "open(%r, 'r').read()" % self.path])

    def test_no_lock_allows_subprocess_read_python3(self):
        # This makes sure that if the default behavior changes or varies
        # between Python versions we catch it.  Without this there's not a way
        # to ensure that test_lock_causes_subprocess_read_failure() is really
        # testing the behavior of LockFileEx()
        subprocess.check_call([
            sys.executable, "-c", "open(%r, 'r').read()" % self.path])


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
            subprocess.check_call([
                sys.executable, "-c", "open(%r, 'r').read()" % self.path])

        UnlockFileEx(self.handle, 0, 1024)

        subprocess.check_call([
            sys.executable, "-c", "open(%r, 'r').read()" % self.path])
