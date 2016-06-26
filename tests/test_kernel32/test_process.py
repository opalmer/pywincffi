import ctypes
import os

from mock import patch

from pywincffi.core import dist
from pywincffi.dev.testutil import TestCase
from pywincffi.exceptions import WindowsAPIError, PyWinCFFINotImplementedError
from pywincffi.kernel32 import process as k32process
from pywincffi.kernel32 import (
    CloseHandle, OpenProcess, GetCurrentProcess, GetExitCodeProcess,
    GetProcessId, pid_exists, TerminateProcess, CreateToolhelp32Snapshot)
from pywincffi.wintypes import HANDLE

try:
    IS_ADMIN = ctypes.windll.shell32.IsUserAnAdmin() != 0
except AttributeError:  # pragma: no cover
    IS_ADMIN = None


class TestOpenProcess(TestCase):
    """
    Tests for :func:`pywincffi.kernel32.OpenProcess`
    """
    def test_returns_handle(self):
        _, library = dist.load()

        handle = OpenProcess(
            library.PROCESS_QUERY_INFORMATION,
            False,
            os.getpid()
        )

        self.assertIsInstance(handle, HANDLE)
        CloseHandle(handle)

    def test_access_denied_for_null_desired_access(self):
        with self.assertRaises(WindowsAPIError) as error:
            OpenProcess(0, False, os.getpid())

        self.assertEqual(error.exception.errno, 5)

    def test_get_process_id_current_process(self):
        # We should be able to access the pid of the process
        # we created a handle to.
        _, library = dist.load()

        handle = OpenProcess(
            library.PROCESS_QUERY_INFORMATION,
            False,
            os.getpid()
        )
        self.assertEqual(GetProcessId(handle), os.getpid())
        CloseHandle(handle)


class TestGetCurrentProcess(TestCase):
    """
    Tests for :func:`pywincffi.kernel32.GetCurrentProcess`
    """
    def test_returns_handle(self):
        handle = GetCurrentProcess()
        self.assertIsInstance(handle, HANDLE)

    def test_returns_same_handle(self):
        # GetCurrentProcess is somewhat special in that it will
        # always return a handle to the same object.  However, __eq__ is not
        # opaque so the string representation of the two handles
        # should always match since it contains the address of the object
        # in memory.
        h1 = GetCurrentProcess()
        h2 = GetCurrentProcess()
        self.assertIsNot(h1, h2)
        self.assertEqual(h1, h2)

    def test_handle_is_current_process(self):
        handle = GetCurrentProcess()
        self.assertEqual(GetProcessId(handle), os.getpid())

    def test_handle_is_valid(self):
        _, library = dist.load()
        handle = OpenProcess(
            library.PROCESS_QUERY_INFORMATION, False, os.getpid())

        # If the handle were invalid, this would fail.
        CloseHandle(handle)


class TestGetProcessId(TestCase):
    """
    Tests for :func:`pywincffi.kernel32.GetProcessId`
    """
    def test_get_pid_of_external_process(self):
        process = self.create_python_process("import time; time.sleep(3)")
        expected_pid = process.pid

        _, library = dist.load()
        handle = OpenProcess(
            library.PROCESS_QUERY_INFORMATION, False, expected_pid)
        self.assertEqual(GetProcessId(handle), expected_pid)
        CloseHandle(handle)


class TestGetExitCodeProcess(TestCase):
    """
    Tests for :func:`pywincffi.kernel32.GetExitCodeProcess`
    """
    def test_get_exit_code_zero(self):
        process = self.create_python_process("import sys; sys.exit(0)")
        pid = process.pid
        process.communicate()

        _, library = dist.load()
        hProcess = OpenProcess(
            library.PROCESS_QUERY_INFORMATION, False, pid)
        self.addCleanup(CloseHandle, hProcess)
        self.assertEqual(GetExitCodeProcess(hProcess), 0)

    def test_get_exit_code_non_zero(self):
        process = self.create_python_process("import sys; sys.exit(1)")
        pid = process.pid
        process.communicate()

        _, library = dist.load()
        hProcess = OpenProcess(
            library.PROCESS_QUERY_INFORMATION, False, pid)
        self.addCleanup(CloseHandle, hProcess)
        self.assertEqual(GetExitCodeProcess(hProcess), 1)

    def test_process_still_active(self):
        process = self.create_python_process("import time; time.sleep(5)")
        pid = process.pid

        _, library = dist.load()
        hProcess = OpenProcess(
            library.PROCESS_QUERY_INFORMATION, False, pid)
        self.addCleanup(CloseHandle, hProcess)
        self.assertEqual(GetExitCodeProcess(hProcess), library.STILL_ACTIVE)


class TestPidExists(TestCase):
    """
    Tests for :func:`pywincffi.kernel32.pid_exists`
    """
    def test_reserved_pids_always_return_true(self):
        for pid in k32process.RESERVED_PIDS:
            self.assertTrue(pid_exists(pid))

    def test_returns_true_if_access_is_denied(self):
        # This will always test for ERROR_ACCESS_DENIED by forcing OpenProcess
        # to not request any permissions
        def open_process(_, bInheritHandle, dwProcessId):
            return OpenProcess(0, bInheritHandle, dwProcessId)

        process = self.create_python_process("import time; time.sleep(5)")
        with patch.object(k32process, "OpenProcess", open_process):
            self.assertTrue(pid_exists(process.pid))

    def test_process_never_existed(self):
        # OpenProcess *might* work even when the process
        # is no longer alive which is why pid_exists() checks
        # for an exit code.  For cases where the process
        # never should have existed however we should
        # expect to get False from pid_exists().  Here
        # we're attempting to do this with something
        # that should probably never exist.
        self.assertFalse(pid_exists(0xFFFFFFFC))

    def test_running_process(self):
        process = self.create_python_process("import time; time.sleep(5)")
        self.assertTrue(
            pid_exists(process.pid))

    def test_process_dies_while_waiting(self):
        # This condition should be very rare because of what the default
        # wait is set to but we check it anyway just in case.
        _, library = dist.load()
        process = self.create_python_process("import time; time.sleep(1)")
        self.assertFalse(pid_exists(process.pid, wait=library.INFINITE))

    def test_returns_false_for_process_with_exit_code_259(self):
        _, library = dist.load()
        process = self.create_python_process(
            "import sys; sys.exit(%d)" % library.STILL_ACTIVE)
        process.communicate()
        self.assertFalse(pid_exists(process.pid))

    def test_raises_unhandled_windows_api_error(self):
        def new_open_process(*args, **kwargs):
            raise WindowsAPIError("", "", 42)

        with patch.object(k32process, "OpenProcess", new_open_process):
            process = \
                self.create_python_process("import time; time.sleep(5)")

            with self.assertRaises(WindowsAPIError):
                self.assertTrue(pid_exists(process.pid))

    def test_raises_not_implemented_for_wait_abandoned(self):
        _, library = dist.load()

        with patch.object(
            k32process, "WaitForSingleObject",
            return_value=library.WAIT_ABANDONED
        ):
            process = \
                self.create_python_process("import time; time.sleep(5)")

            with self.assertRaises(PyWinCFFINotImplementedError):
                self.assertTrue(pid_exists(process.pid))

    def test_raises_not_implemented_for_other_wait_result(self):
        with patch.object(k32process, "WaitForSingleObject", return_value=42):
            process = \
                self.create_python_process("import time; time.sleep(5)")

            with self.assertRaises(PyWinCFFINotImplementedError):
                self.assertTrue(pid_exists(process.pid))

    def test_calls_closehandle(self):
        with patch.object(k32process, "CloseHandle") as mocked:
            process = \
                self.create_python_process("import time; time.sleep(5)")

            self.assertTrue(pid_exists(process.pid))

        self.assertEqual(mocked.call_count, 1)


class TestTerminateProcess(TestCase):
    """
    Tests for :func:`pywincffi.kernel32.TerminateProcess`
    """
    def test_terminates_process(self):
        process = self.create_python_process("import time; time.sleep(5)")
        _, library = dist.load()

        handle = OpenProcess(library.PROCESS_TERMINATE, False, process.pid)
        self.addCleanup(CloseHandle, handle)
        TerminateProcess(handle, 42)
        process.communicate()
        self.assertEqual(process.returncode, 42)


class TestCreateToolhelp32Snapshot(TestCase):
    """
    Tests for :func:`pywincffi.kernel32.CreateToolhelp32Snapshot`
    """
    def test_get_process_list(self):
        _, library = dist.load()

        handle = CreateToolhelp32Snapshot(library.TH32CS_SNAPPROCESS, 0)
        self.addCleanup(CloseHandle, handle)

    def test_invalid_process(self):
        _, library = dist.load()

        with self.assertRaises(WindowsAPIError):
            CreateToolhelp32Snapshot(library.TH32CS_SNAPPROCESS, 3)
