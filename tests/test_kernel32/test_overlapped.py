import os
import shutil
import tempfile

from six import text_type

from pywincffi.dev.testutil import TestCase

from pywincffi.core import dist

from pywincffi.kernel32 import (
    CreateFile, WriteFile, CloseHandle, CreateEvent, GetOverlappedResult)
from pywincffi.wintypes import OVERLAPPED


class TestOverlappedWriteFile(TestCase):
    """
    Tests for :func:`pywincffi.kernel32.GetOverlappedResult`
    """
    def test_overlapped_write_file(self):
        # Test outline:
        # - Create a temp dir.
        # - CreateFile for writing with FILE_FLAG_OVERLAPPED.
        # - WriteFile in overlapped mode.
        # - Use GetOverlappedResult to wait for IO completion.

        temp_dir = tempfile.mkdtemp(prefix="pywincffi-test-ovr-")
        self.addCleanup(shutil.rmtree, temp_dir, ignore_errors=True)

        filename = text_type(os.path.join(temp_dir, "overlapped-write-file"))
        file_contents = b"hello overlapped world"

        _, lib = dist.load()
        handle = CreateFile(
            lpFileName=filename,
            dwDesiredAccess=lib.GENERIC_WRITE,
            dwCreationDisposition=lib.CREATE_NEW,
            dwFlagsAndAttributes=lib.FILE_FLAG_OVERLAPPED,
        )

        # Prepare overlapped write
        ovr = OVERLAPPED()
        ovr.hEvent = CreateEvent(bManualReset=True, bInitialState=False)

        # Go for overlapped WriteFile. Should result in:
        # - num_bytes_written == 0
        # - GetLastError() == ERROR_IO_PENDING

        # HOWEVER, https://msdn.microsoft.com/en-us/library/aa365683 states:
        # "Further, the WriteFile function will sometimes return TRUE with a
        # GetLastError value of ERROR_SUCCESS, even though it is using an
        # asynchronous handle (which can also return FALSE with
        # ERROR_IO_PENDING).
        # Test strategy:
        # - Disregard WriteFile return result.
        # - Assert GetLastError is either ERROR_IO_PENDING or ERROR_SUCCESS.
        # - Later validate that the correct number of bytes was written.

        _ = WriteFile(handle, file_contents, lpOverlapped=ovr)
        self.maybe_assert_last_error(lib.ERROR_IO_PENDING)

        # Block until async write is completed.
        num_bytes_written = GetOverlappedResult(handle, ovr, bWait=True)
        self.assertEqual(num_bytes_written, len(file_contents))

        CloseHandle(handle)
