import os
import shutil
import tempfile

from pywincffi.dev.testutil import TestCase

from pywincffi.core import dist

from pywincffi.kernel32 import (
    CreateFile, WriteFile, FlushFileBuffers, CloseHandle,
    CreateEvent, GetOverlappedResult, WaitForSingleObject)
from pywincffi.wintypes import OVERLAPPED


class TestOverlappedWriteFile(TestCase):
    """
    Tests for :func:`pywincffi.kernel32.GetOverlappedResult`
    """
    def test_overlapped_write_binary(self):
        base_dir = tempfile.mkdtemp(prefix="pywincffi-test-ovr-")
        self.addCleanup(shutil.rmtree, base_dir, ignore_errors=True)
        base_filename = "test-overlapped-write-file"
        filename = unicode(os.path.join(base_dir, base_filename))

        _, lib = dist.load()
        handle = CreateFile(
            lpFileName=filename,
            dwDesiredAccess=lib.GENERIC_WRITE,
            dwShareMode=0,
            lpSecurityAttributes=None,
            dwCreationDisposition=lib.CREATE_NEW,
            dwFlagsAndAttributes=lib.FILE_FLAG_OVERLAPPED,
            hTemplateFile=None,
        )

        bytes_to_write = b"hello world"
        ovr = OVERLAPPED()
        event = CreateEvent(bManualReset=True, bInitialState=False)
        ovr.hEvent = event
        nbw = WriteFile(handle, bytes_to_write, lpOverlapped=ovr)
        self.assertEqual(nbw, 0)  # async in progress returns 0

        nbw = GetOverlappedResult(handle, ovr, bWait=True)
        self.assertEqual(nbw, len(bytes_to_write))

        CloseHandle(handle)
