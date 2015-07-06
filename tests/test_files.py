from mock import patch

from pywincffi.core.testutil import TestCase
from pywincffi.exceptions import WindowsAPIError
from pywincffi.kernel32.files import CreatePipe, CloseHandle, WriteFile


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


class AnonymousPipeFileTest(TestCase):
    """
    Basic tests for :func:`pywincffi.files.WritePipe` and
    :func:`pywincffi.files.ReadPipe`
    """
    def test_bytes_written(self):
        reader, writer = CreatePipe()
        data = "hello world"
        bytes_written = WriteFile(writer, data)
        self.assertEqual(bytes_written, len(data) * 2)

    # TODO: tests for ReadFile on `reader`