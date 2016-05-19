import os
import ctypes
import tempfile
import subprocess
import sys
from os.path import isfile

from mock import patch
from six import PY3

from pywincffi.core import dist
from pywincffi.dev.testutil import (
    TestCase, skip_unless_python2, skip_unless_python3)
from pywincffi.exceptions import WindowsAPIError

from pywincffi.kernel32 import file as _file  # used for mocks
from pywincffi.kernel32 import (
    CreateFile, CloseHandle, MoveFileEx, WriteFile, FlushFileBuffers,
    LockFileEx, UnlockFileEx, handle_from_file)


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

    @skip_unless_python2
    def test_python2_write_string(self):
        handle, path = self.create_handle()
        WriteFile(
            handle, "hello world", lpBufferType="char[]")
        FlushFileBuffers(handle)
        with open(path, "r") as file_:
            self.assertEqual(file_.read(), "hello world\x00")

    @skip_unless_python2
    def test_python2_write_unicode(self):
        handle, path = self.create_handle()
        WriteFile(handle, u"hello world")
        FlushFileBuffers(handle)
        with open(path, "r") as file_:
            self.assertEqual(
                file_.read(),
                "h\x00e\x00l\x00l\x00o\x00 \x00w\x00o\x00r\x00l"
                "\x00d\x00\x00\x00")

    @skip_unless_python3
    def test_python3_write_string(self):
        handle, path = self.create_handle()
        WriteFile(handle, "hello world")
        FlushFileBuffers(handle)
        v = b"h\x00e\x00l\x00l\x00o\x00 \x00w\x00o\x00r\x00l\x00d\x00\x00\x00"
        with open(path, "rb") as file_:
            self.assertEqual(file_.read(), v)

    @skip_unless_python3
    def test_python3_write_bytes(self):
        handle, path = self.create_handle()
        WriteFile(handle, b"hello world", lpBufferType="char[]")
        FlushFileBuffers(handle)
        with open(path, "rb") as file_:
            self.assertEqual(file_.read(), b"hello world\x00")


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

        MoveFileEx(path1, path2)

        with open(path2, "r") as file_:
            self.assertEqual(file_.read(), file_contents)

        self.assertFalse(isfile(path1))

    def test_run_delete_after_reboot(self):
        fd, path = tempfile.mkstemp()
        os.close(fd)

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
            handle = CreateFile(
                path, 0, dwCreationDisposition=library.CREATE_ALWAYS)
            self.addCleanup(CloseHandle, handle)

        # If we've made it this far, the exception was ignored by CreateFile

    def test_raises_other_errors_for_create_always(self):
        _, library = dist.load()

        with self.assertRaises(WindowsAPIError) as error:
            handle = CreateFile(
                "", 0, dwCreationDisposition=library.CREATE_ALWAYS)
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
        self.handle = CreateFile(path, library.GENERIC_WRITE)
        self.addCleanup(CloseHandle, self.handle)

        if PY3:
            lpBufferType = "wchar_t[]"
        else:
            lpBufferType = "char[]"

        WriteFile(self.handle, "hello", lpBufferType=lpBufferType)


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
