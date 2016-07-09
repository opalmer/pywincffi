import ctypes
import os
import sys

from mock import patch
from six import text_type

from pywincffi.core import dist
from pywincffi.dev.testutil import TestCase, mock_library
from pywincffi.exceptions import (
    WindowsAPIError, PyWinCFFINotImplementedError, InputError)
from pywincffi.kernel32 import process as k32process
from pywincffi.kernel32 import (
    CloseHandle, OpenProcess, GetCurrentProcess, GetExitCodeProcess,
    GetProcessId, TerminateProcess, CreateToolhelp32Snapshot, CreateProcess,
    pid_exists)

# A couple of internal imports.  These are not considered part of the public
# API but we still need to test them.
from pywincffi.kernel32.process import environment_to_string, module_name
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
        self.SetLastError(0)

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


class TestEnvironmentToString(TestCase):
    """
    Tests for :func:`pywincffi.kernel32.process.environment_to_string`
    """
    def test_non_dict_iteritems(self):
        class NonDictIterItems(object):
            def iteritems(self):
                yield (u"a", u"b")
                yield (u"c", u"d")

        self.assertEqual(
            environment_to_string(NonDictIterItems()),
            u"a=b\0c=d"
        )

    def test_non_dict_items(self):
        class NonDictItems(object):
            def items(self):
                yield (u"e", u"f")
                yield (u"g", u"h")

        self.assertEqual(
            environment_to_string(NonDictItems()),
            u"e=f\0g=h"
        )

    def test_type_check_for_environment_key(self):
        with self.assertRaisesRegex(InputError, ".*for environment key 1.*"):
            environment_to_string({1: 1})

    def test_type_check_for_environment_value(self):
        with self.assertRaisesRegex(InputError, ".*environment value 2.*"):
            environment_to_string({u"2": 2})

    def test_key_cannot_contain_equals(self):
        with self.assertRaisesRegex(InputError, ".*cannot contain the `=`.*"):
            environment_to_string({u"3=4": u""})


class TestModuleName(TestCase):
    """
    Tests for :func:`pywincffi.kernel32.process.module_name`
    """
    def test_module_name_conversion(self):
        # NOTE: Use \\ for all paths, the test itself will try the alternate
        # path separator.
        cases = {
            u"C:\\foo.exe": u"C:\\foo.exe",
            u"'C:\\foo.exe' -c 'hello world'": u"C:\\foo.exe",
            u'"C:\\foo.exe" -c "hello world"': u"C:\\foo.exe",
            u'"C:\\foo.exe" -c \'hello world\'': u"C:\\foo.exe",
            u'"C:\\foo\'s.exe" -c \'hello world\'': u"C:\\foo\'s.exe",
            u'"C:\\foo.exe -c \'hello world\'': u"C:\\foo.exe",
            u'"C:\\Some Path\\foo.exe" -c \'hello world\'':
                u"C:\\Some Path\\foo.exe",

            # The below are what would probably be considered broken
            # input.  A human should not have trouble picking out the
            # module name but a computer would since it's just tokenizing
            # the input.  module_name() itself though will just let it pass
            # through which should result in the call to CreateProcess
            # eventually failing (better to fail further down the chain then
            # have to debug some internal conversion that pywincffi is doing).
            u'"C:\\Some Path\\foo.exe -c \'hello world\'':
                u"C:\\Some",
            u'"C:\\Some Path\\foo.exe -c \"hello world\'':
                u"C:\\Some Path\\foo.exe -c ",
        }

        for path, expected in cases.items():
            # First try it with escaped paths
            self.assertEqual(module_name(path), expected)

            # Now with / instead of \\
            self.assertEqual(
                module_name(path.replace("\\", "/")),
                expected.replace("\\", "/"))

    def test_failed_to_determine_module_name(self):
        with self.assertRaises(InputError):
            module_name(u" ")


class TestCreateProcess(TestCase):
    """
    Tests for :func:`pywincffi.kernel32.CreateProcess`
    """
    @classmethod
    def NoOpCreateProcess(cls, *args):
        pass

    def test_lpCommandLine_length_max_command_line(self):
        with mock_library(CreateProcess=self.NoOpCreateProcess):
            _, library = dist.load()

            match = ".*cannot exceed %s.*" % library.MAX_COMMAND_LINE
            with self.assertRaisesRegex(InputError, match):
                CreateProcess(u" " * (library.MAX_COMMAND_LINE + 1))

    def test_lpCommandLine_length_max_path(self):
        with mock_library(CreateProcess=self.NoOpCreateProcess):
            _, library = dist.load()

            match = ".*cannot exceed %s.*" % library.MAX_PATH
            with self.assertRaisesRegex(InputError, match):
                CreateProcess(
                    u"'%s' arg1" % self.random_string(library.MAX_PATH + 1))

    def test_basic_call(self):
        value = text_type(self.random_string(6))
        environment = {u"KEY": value}
        command = text_type("'%s' -c 'import os'" % sys.executable)

        try:
            result = CreateProcess(
                command, lpApplicationName=text_type(sys.executable),
                # lpEnvironment=environment
            )
        except WindowsAPIError:
            pass
            # ffi, _ = dist.load()
            # errno, error_message = ffi.getwinerror()
            # self.fail()
