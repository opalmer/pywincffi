try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from pywincffi.core.testutil import TestCase
from pywincffi.exceptions import WindowsAPIError
from pywincffi.kernel32.files import (
    CreatePipe, CloseHandle, WriteFile, ReadFile)


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
        self.addCleanup(CloseHandle, reader)
        self.addCleanup(CloseHandle, writer)

        data = b"hello world".decode("utf-8")
        bytes_written = WriteFile(writer, data)
        self.assertEqual(bytes_written, len(data) * 2)

    def test_bytes_read(self):
        reader, writer = CreatePipe()
        self.addCleanup(CloseHandle, reader)
        self.addCleanup(CloseHandle, writer)

        data = b"hello world".decode("utf-8")
        data_written = WriteFile(writer, data)

        read_data = ReadFile(reader, data_written)
        self.assertEqual(data, read_data)