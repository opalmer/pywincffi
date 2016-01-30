import ctypes
import os
import subprocess
import sys

from pywincffi.core import dist
from pywincffi.dev.testutil import TestCase
from pywincffi.exceptions import WindowsAPIError
from pywincffi.kernel32.process import RESERVED_PIDS
from pywincffi.kernel32 import (
    CloseHandle, OpenProcess, GetCurrentProcess, GetExitCodeProcess,
    GetProcessId, pid_exists)

try:
    IS_ADMIN = ctypes.windll.shell32.IsUserAnAdmin() != 0
except AttributeError:  # pragma: no cover
    IS_ADMIN = None


class TestOpenProcess(TestCase):
    """
    Tests for :func:`pywincffi.kernel32.OpenProcess`
    """
    def test_returns_handle(self):
        ffi, library = dist.load()

        handle = OpenProcess(
            library.PROCESS_QUERY_INFORMATION,
            False,
            os.getpid()
        )

        typeof = ffi.typeof(handle)
        self.assertEqual(typeof.kind, "pointer")
        self.assertEqual(typeof.cname, "void *")
        CloseHandle(handle)

    def test_access_denied_for_null_desired_access(self):
        with self.assertRaises(WindowsAPIError) as error:
            OpenProcess(0, False, os.getpid())

        self.assertEqual(error.exception.code, 5)

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
        ffi, _ = dist.load()
        handle = GetCurrentProcess()
        typeof = ffi.typeof(handle)
        self.assertEqual(typeof.kind, "pointer")
        self.assertEqual(typeof.cname, "void *")

    def test_returns_same_handle(self):
        # GetCurrentProcess is somewhat special in that it will
        # always return a handle to the same object.  However, __eq__ is not
        # opaque so the string representation of the two handles
        # should always match since it contains the address of the object
        # in memory.
        self.assertEqual(repr(GetCurrentProcess()), repr(GetCurrentProcess()))

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
        for pid in RESERVED_PIDS:
            self.assertTrue(pid_exists(pid))

    def test_returns_true_if_access_is_denied(self):
        # It only makes sense to run this test if we're
        # not an administrator.  Otherwise we'd have
        # access to the process in question.
        if IS_ADMIN:
            self.skipTest("Non-Administrator only test")

        # Find a system process which is something
        output = subprocess.check_output(
            ["tasklist", "/V", "/NH", "/FI", "IMAGENAME eq lsass.exe"])

        for line in output.splitlines():
            split = line.split()
            if not split:
                continue
            pid = split[1]
            break
        else:
            self.fail("Failed to locate pid for lsass.exe")

        self.assertTrue(pid_exists(int(pid)))

    def test_process_never_existed(self):
        # OpenProcess *might* work even when the process
        # is no longer alive which is why pid_exists() checks
        # for an exit code.  For cases where the process
        # never should have existed however we should
        # expect to get False from pid_exists().  Here
        # we're attempting to do this with something
        # that should probably never exist.
        self.assertFalse(pid_exists(0xFFFFFFFC))

    # def test_returns_true_for_running_process(self):
    #     process = subprocess.Popen(
    #         [sys.executable, "-c", "import time; time.sleep(5)"]
    #     )
    #     self.addCleanup(process.terminate)
    #     pid = process.pid
    #     self.assertTrue(pid_exists(pid))


