from pywincffi.core import dist
from pywincffi.dev.testutil import TestCase
from pywincffi.exceptions import WindowsAPIError
from pywincffi.kernel32 import CloseHandle, OpenProcess, WaitForSingleObject


class TestWaitForSingleObject(TestCase):
    """
    Tests for :func:`pywincffi.kernel32.WaitForSingleObject`
    """
    def test_wait_failed(self):
        # This should cause WAIT_FAILED to be returned by the underlying
        # WaitForSingleObject because we didn't request the SYNCHRONIZE
        # permission.
        process = self.create_python_process("import time; time.sleep(3)")
        _, library = dist.load()

        hProcess = OpenProcess(
            library.PROCESS_QUERY_INFORMATION, False, process.pid)
        self.addCleanup(CloseHandle, hProcess)

        with self.assertRaises(WindowsAPIError) as exec_:
            WaitForSingleObject(hProcess, 3)
            self.assertEqual(exec_.code, library.WAIT_FAILED)

    def test_wait_on_running_process(self):
        process = self.create_python_process("import time; time.sleep(1)")
        _, library = dist.load()

        hProcess = OpenProcess(
            library.PROCESS_QUERY_INFORMATION | library.SYNCHRONIZE,
            False, process.pid)
        self.addCleanup(CloseHandle, hProcess)
        self.assertEqual(
            WaitForSingleObject(hProcess, 0), library.WAIT_TIMEOUT)

    def test_process_dies_before_timeout(self):
        process = self.create_python_process("import time; time.sleep(1)")
        _, library = dist.load()

        hProcess = OpenProcess(
            library.PROCESS_QUERY_INFORMATION | library.SYNCHRONIZE,
            False, process.pid)
        self.addCleanup(CloseHandle, hProcess)
        self.assertEqual(
            WaitForSingleObject(hProcess, library.INFINITE),
            library.WAIT_OBJECT_0)
