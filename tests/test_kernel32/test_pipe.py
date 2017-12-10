from pywincffi.dev.testutil import TestCase
from pywincffi.exceptions import WindowsAPIError
from pywincffi.kernel32 import (
    CreatePipe, PeekNamedPipe, PeekNamedPipeResult, ReadFile, WriteFile,
    CloseHandle, SetNamedPipeHandleState)
from pywincffi.core import dist

# For pylint on non-windows platforms
try:
    WindowsError
except NameError:
    WindowsError = OSError  # pylint: disable=redefined-builtin


class PipeBaseTestCase(TestCase):
    def create_anonymous_pipes(self):
        reader, writer = CreatePipe()
        self.addCleanup(CloseHandle, reader)
        self.addCleanup(CloseHandle, writer)
        return reader, writer


class CreatePipeTest(TestCase):
    """
    Basic tests for :func:`pywincffi.kernel32.CreatePipe` and
    :func:`pywincffi.kernel32.CloseHandle`
    """
    def test_create_and_close_pipes(self):
        reader, writer = CreatePipe()

        CloseHandle(writer)

        # Second attempt should fail
        with self.assertRaises(WindowsAPIError):
            CloseHandle(writer)

        _, library = dist.load()
        self.assert_last_error(library.ERROR_INVALID_HANDLE)

        # Second attempt should fail
        CloseHandle(reader)
        with self.assertRaises(WindowsAPIError):
            CloseHandle(reader)

        self.assert_last_error(library.ERROR_INVALID_HANDLE)


class AnonymousPipeReadWriteTest(PipeBaseTestCase):
    """
    Basic tests for :func:`pywincffi.kernel32.WritePipe` and
    :func:`pywincffi.kernel32.ReadPipe`
    """
    def test_python_bytes(self):
        reader, writer = self.create_anonymous_pipes()

        data = b"hello world"
        bytes_written = WriteFile(writer, data)
        buf = bytearray(bytes_written)
        read = ReadFile(reader, buf, bytes_written)
        self.assertEqual(bytes_written, read)
        self.assertEqual(buf, bytearray(b"hello world"))

        _, library = dist.load()
        self.maybe_assert_last_error(library.ERROR_INVALID_HANDLE)


# TODO: tests for lpBuffer from the result
class TestPeekNamedPipe(PipeBaseTestCase):
    """
    Tests for :func:`pywincffi.kernel32.PeekNamedPipe`.
    """
    def test_return_type(self):
        reader, _ = self.create_anonymous_pipes()
        self.assertIsInstance(PeekNamedPipe(reader, 0), PeekNamedPipeResult)
        _, library = dist.load()
        self.maybe_assert_last_error(library.ERROR_INVALID_HANDLE)

    def test_peek_does_not_remove_data(self):
        reader, writer = self.create_anonymous_pipes()

        data = b"hello world"
        data_written = WriteFile(writer, data)
        buf = bytearray(data_written)
        read = ReadFile(reader, buf, data_written)
        self.assertEqual(read, data_written)
        PeekNamedPipe(reader, 0)
        self.assertEqual(buf, bytearray(data))
        _, library = dist.load()
        self.maybe_assert_last_error(library.ERROR_INVALID_HANDLE)

    def test_bytes_read_less_than_bytes_written(self):
        reader, writer = self.create_anonymous_pipes()

        data = b"hello world"
        WriteFile(writer, data)

        result = PeekNamedPipe(reader, 1)
        self.assertEqual(result.lpBytesRead, 1)
        _, library = dist.load()
        self.maybe_assert_last_error(library.ERROR_INVALID_HANDLE)

    def test_bytes_read_greater_than_bytes_written(self):
        reader, writer = self.create_anonymous_pipes()

        data = b"hello world"
        bytes_written = WriteFile(writer, data)

        result = PeekNamedPipe(reader, bytes_written * 2)
        self.assertEqual(result.lpBytesRead, bytes_written)
        _, library = dist.load()
        self.maybe_assert_last_error(library.ERROR_INVALID_HANDLE)

    def test_total_bytes_avail(self):
        reader, writer = self.create_anonymous_pipes()

        data = b"hello world"
        bytes_written = WriteFile(writer, data)

        result = PeekNamedPipe(reader, 0)
        self.assertEqual(result.lpTotalBytesAvail, bytes_written)
        _, library = dist.load()
        self.maybe_assert_last_error(library.ERROR_INVALID_HANDLE)

    def test_total_bytes_avail_after_read(self):
        reader, writer = self.create_anonymous_pipes()

        data = b"hello world"
        bytes_written = WriteFile(writer, data)

        read_bytes = 7
        buf = bytearray(read_bytes)
        read = ReadFile(reader, buf, read_bytes)
        self.assertEqual(read, read_bytes)

        result = PeekNamedPipe(reader, 0)
        self.assertEqual(
            result.lpTotalBytesAvail, bytes_written - read_bytes)
        _, library = dist.load()
        self.maybe_assert_last_error(library.ERROR_INVALID_HANDLE)


class TestSetNamedPipeHandleState(PipeBaseTestCase):
    """
    Tests for :func:`pywincffi.kernel32.SetNamedPipeHandleState`.
    """
    def _set_mode(self, readmode):
        reader, _ = self.create_anonymous_pipes()
        SetNamedPipeHandleState(reader, lpMode=readmode)

    def test_mode_null(self):
        self._set_mode(None)

    def test_mode_byte(self):
        _, lib = dist.load()
        self._set_mode(lib.PIPE_READMODE_BYTE)

    def test_mode_message_fails(self):
        _, lib = dist.load()
        # should fail: anonymous pipes are byte oriented
        with self.assertRaises(WindowsAPIError):
            self._set_mode(lib.PIPE_READMODE_MESSAGE)

        self.assert_last_error(lib.ERROR_INVALID_PARAMETER)

    def test_mode_wait(self):
        _, lib = dist.load()
        self._set_mode(lib.PIPE_WAIT)

    def test_mode_nowait(self):
        _, lib = dist.load()
        self._set_mode(lib.PIPE_NOWAIT)

    def _set_max_collection_count(self, count):
        _, writer = self.create_anonymous_pipes()
        SetNamedPipeHandleState(writer, lpMaxCollectionCount=count)

    def test_max_collection_count_null(self):
        self._set_max_collection_count(None)

    def test_max_collection_count_fail(self):
        # should fail: only supported with named pipes
        with self.assertRaises(WindowsAPIError):
            self._set_max_collection_count(10)

        _, library = dist.load()
        self.assert_last_error(library.ERROR_INVALID_PARAMETER)

    def _set_collect_data_timeout(self, timeout):
        reader, _ = self.create_anonymous_pipes()
        SetNamedPipeHandleState(reader, lpCollectDataTimeout=timeout)

    def test_collect_data_timeout_null(self):
        self._set_collect_data_timeout(None)

    def test_collect_data_timeout_fail(self):
        # should fail: only supported with named pipes
        with self.assertRaises(WindowsAPIError):
            self._set_collect_data_timeout(500)

        _, library = dist.load()
        self.assert_last_error(library.ERROR_INVALID_PARAMETER)
