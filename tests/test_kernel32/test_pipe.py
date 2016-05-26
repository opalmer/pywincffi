from pywincffi.dev.testutil import TestCase
from pywincffi.exceptions import WindowsAPIError
from pywincffi.kernel32 import (
    CreatePipe, PeekNamedPipe, PeekNamedPipeResult, ReadFile, WriteFile,
    CloseHandle)

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

        # Second attempt should fail
        CloseHandle(reader)
        with self.assertRaises(WindowsAPIError):
            CloseHandle(reader)


class AnonymousPipeReadWriteTest(PipeBaseTestCase):
    """
    Basic tests for :func:`pywincffi.kernel32.WritePipe` and
    :func:`pywincffi.kernel32.ReadPipe`
    """
    def test_python_bytes(self):
        reader, writer = self.create_anonymous_pipes()

        data = b"hello world"
        bytes_written = WriteFile(writer, data)
        self.assertEqual(
            ReadFile(reader, bytes_written),
            b"hello world")


# TODO: tests for lpBuffer from the result
class TestPeekNamedPipe(PipeBaseTestCase):
    """
    Tests for :func:`pywincffi.kernel32.PeekNamedPipe`.
    """
    def test_return_type(self):
        reader, _ = self.create_anonymous_pipes()
        self.assertIsInstance(PeekNamedPipe(reader, 0), PeekNamedPipeResult)

    def test_peek_does_not_remove_data(self):
        reader, writer = self.create_anonymous_pipes()

        data = b"hello world"
        data_written = WriteFile(writer, data)

        PeekNamedPipe(reader, 0)
        self.assertEqual(ReadFile(reader, data_written), data)

    def test_bytes_read_less_than_bytes_written(self):
        reader, writer = self.create_anonymous_pipes()

        data = b"hello world"
        WriteFile(writer, data)

        result = PeekNamedPipe(reader, 1)
        self.assertEqual(result.lpBytesRead, 1)

    def test_bytes_read_greater_than_bytes_written(self):
        reader, writer = self.create_anonymous_pipes()

        data = b"hello world"
        bytes_written = WriteFile(writer, data)

        result = PeekNamedPipe(reader, bytes_written * 2)
        self.assertEqual(result.lpBytesRead, bytes_written)

    def test_total_bytes_avail(self):
        reader, writer = self.create_anonymous_pipes()

        data = b"hello world"
        bytes_written = WriteFile(writer, data)

        result = PeekNamedPipe(reader, 0)
        self.assertEqual(result.lpTotalBytesAvail, bytes_written)

    def test_total_bytes_avail_after_read(self):
        reader, writer = self.create_anonymous_pipes()

        data = b"hello world"
        bytes_written = WriteFile(writer, data)

        read_bytes = 7
        ReadFile(reader, read_bytes)

        result = PeekNamedPipe(reader, 0)
        self.assertEqual(
            result.lpTotalBytesAvail, bytes_written - read_bytes)
