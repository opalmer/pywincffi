from pywincffi.dev.testutil import (
    TestCase, skip_unless_python3, skip_unless_python2)
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
    @skip_unless_python3
    def test_python_3_bytes(self):
        reader, writer = self.create_anonymous_pipes()

        data = b"hello world"
        bytes_written = WriteFile(writer, data, lpBufferType="char[]")
        self.assertEqual(
            ReadFile(reader, bytes_written).encode("utf-8"),
            b"\xe6\x95\xa8\xe6\xb1\xac\xe2\x81\xaf\xe6\xbd\xb7\xe6\xb1\xb2d")

    @skip_unless_python3
    def test_python3_string(self):
        reader, writer = self.create_anonymous_pipes()

        data = "hello world"
        bytes_written = WriteFile(writer, data)
        self.assertEqual(
            ReadFile(reader, bytes_written).encode("utf-8"),
            b"hello world")

    @skip_unless_python2
    def test_python2_unicode(self):
        reader, writer = self.create_anonymous_pipes()

        data = u"hello world"
        bytes_written = WriteFile(writer, data, lpBufferType="wchar_t[]")
        self.assertEqual(
            ReadFile(reader, bytes_written).encode("utf-8"), data)

    @skip_unless_python2
    def test_python2_string(self):
        reader, writer = self.create_anonymous_pipes()

        data = "hello world".encode("utf-8")
        bytes_written = WriteFile(writer, data, lpBufferType="char[]")
        value = u"\u6568\u6c6c\u206f\u6f77\u6c72d"
        self.assertEqual(ReadFile(reader, bytes_written), value)


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
