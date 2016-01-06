import os
import tempfile
from errno import EBADF

from pywincffi.core import dist
from pywincffi.core.testutil import TestCase
from pywincffi.exceptions import WindowsAPIError, InputError
from pywincffi.kernel32.io import (
    CreatePipe, CloseHandle, WriteFile, ReadFile, GetStdHandle,
    PeekNamedPipe, PeekNamedPipeResult, handle_from_file)

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
    Basic tests for :func:`pywincffi.files.CreatePipe` and
    :func:`pywincffi.files.CloseHandle`
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
    Basic tests for :func:`pywincffi.files.WritePipe` and
    :func:`pywincffi.files.ReadPipe`
    """
    def test_bytes_written(self):
        _, writer = self.create_anonymous_pipes()

        data = b"hello world".decode("utf-8")
        bytes_written = WriteFile(writer, data)
        self.assertEqual(bytes_written, len(data) * 2)

    def test_bytes_read(self):
        reader, writer = self.create_anonymous_pipes()

        data = b"hello world".decode("utf-8")
        data_written = WriteFile(writer, data)

        read_data = ReadFile(reader, data_written)
        self.assertEqual(data, read_data)

    def test_partial_bytes_read(self):
        reader, writer = self.create_anonymous_pipes()

        data = b"hello world".decode("utf-8")
        WriteFile(writer, data)

        read_data = ReadFile(reader, 5)
        self.assertEqual(read_data, "hello")

        read_data = ReadFile(reader, 6)
        self.assertEqual(read_data, " world")

    def test_read_more_bytes_than_written(self):
        reader, writer = self.create_anonymous_pipes()

        data = b"hello world".decode("utf-8")
        data_written = WriteFile(writer, data)

        read_data = ReadFile(reader, data_written * 2)
        self.assertEqual(data, read_data)


# TODO: tests for lpBuffer from the result
class TestPeekNamedPipe(PipeBaseTestCase):
    """
    Tests for :func:`pywincffi.kernel32.io.PeekNamedPipe`.
    """
    def test_return_type(self):
        reader, _ = self.create_anonymous_pipes()
        self.assertIsInstance(PeekNamedPipe(reader, 0), PeekNamedPipeResult)

    def test_peek_does_not_remove_data(self):
        reader, writer = self.create_anonymous_pipes()

        data = b"hello world".decode("utf-8")
        data_written = WriteFile(writer, data)

        PeekNamedPipe(reader, 0)
        self.assertEqual(ReadFile(reader, data_written), data)

    def test_bytes_read_less_than_bytes_written(self):
        reader, writer = self.create_anonymous_pipes()

        data = b"hello world".decode("utf-8")
        WriteFile(writer, data)

        result = PeekNamedPipe(reader, 1)
        self.assertEqual(result.lpBytesRead, 1)

    def test_bytes_read_greater_than_bytes_written(self):
        reader, writer = self.create_anonymous_pipes()

        data = b"hello world".decode("utf-8")
        bytes_written = WriteFile(writer, data)

        result = PeekNamedPipe(reader, bytes_written * 2)
        self.assertEqual(result.lpBytesRead, bytes_written)

    def test_total_bytes_avail(self):
        reader, writer = self.create_anonymous_pipes()

        data = b"hello world".decode("utf-8")
        bytes_written = WriteFile(writer, data)

        result = PeekNamedPipe(reader, 0)
        self.assertEqual(result.lpTotalBytesAvail, bytes_written)

    def test_total_bytes_avail_after_read(self):
        reader, writer = self.create_anonymous_pipes()

        data = b"hello world".decode("utf-8")
        bytes_written = WriteFile(writer, data)

        read_bytes = 7
        ReadFile(reader, read_bytes)

        result = PeekNamedPipe(reader, 0)
        self.assertEqual(
            result.lpTotalBytesAvail, bytes_written - (read_bytes * 2))


class TestGetStdHandle(TestCase):
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
