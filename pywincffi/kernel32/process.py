"""
Process
-------

Provides functions, constants and utilities that wrap the Windows
functions associated with process management and interaction.  This
module also provides several constants as well, see Microsoft's
documentation for the constant names and their purpose:

    * **Process Security and Access Rights** -
      https://msdn.microsoft.com/en-us/library/windows/desktop/ms684880

.. note::

    Not all constants may be defined
"""

from six import integer_types

from pywincffi.core import dist
from pywincffi.core.checks import Enums, input_check, error_check
from pywincffi.exceptions import WindowsAPIError, PyWinCFFINotImplementedError
from pywincffi.kernel32.handle import CloseHandle
from pywincffi.kernel32.synchronization import WaitForSingleObject
from pywincffi.wintypes import HANDLE, wintype_to_cdata

RESERVED_PIDS = set([0, 4])


def pid_exists(pid, wait=0):
    """
    Returns True if there's a process associated with ``pid``.

    :param int pid:
        The id of the process to check for.

    :keyword int wait:
        An optional keyword that controls how long we tell
        :func:`WaitForSingleObject` to wait on the process.

    :raises ValidationError:
        Raised if there's a problem with the value provided for ``pid``.
    """
    input_check("pid", pid, integer_types)

    # Process IDs which always exist shouldn't need to continue
    # further.
    if pid in RESERVED_PIDS:
        return True

    _, library = dist.load()

    try:
        hProcess = OpenProcess(
            library.PROCESS_QUERY_INFORMATION | library.SYNCHRONIZE,
            False, pid)

    except WindowsAPIError as error:
        # If we can't access the process then it must exist
        # otherwise there would be nothing to access.  We
        # reach this bit of code if the pid in question
        # is owned by another user or the system and
        # the process running this code does not have the
        # rights to query the other process's information.
        if error.errno == library.ERROR_ACCESS_DENIED:
            return True

        # Sometimes the PID we're asking about no longer exists
        # in the stack anywhere so we'll get ERROR_INVALID_PARAMETER
        # so there's not any reason to continue further.
        if error.errno == library.ERROR_INVALID_PARAMETER:
            return False

        raise

    try:
        process_exit_code = GetExitCodeProcess(hProcess)

        # Process may or may not still be running.  If process_exit_code
        # seem to indicate the process is still alive then run one
        # last check to be certain.
        if process_exit_code == library.STILL_ACTIVE:
            wait_result = WaitForSingleObject(hProcess, wait)

            # The process was still running.
            if wait_result == library.WAIT_TIMEOUT:
                return True

            # The process exited while we were waiting
            # on it so it no longer exists.
            elif wait_result == library.WAIT_OBJECT_0:
                return False

            elif wait_result == library.WAIT_ABANDONED:
                raise PyWinCFFINotImplementedError(
                    "An unknown error occurred while running "
                    "pid_exists(%r).  It appears that the call to "
                    "WaitForSingleObject may be been terminated." % pid)

            else:
                raise PyWinCFFINotImplementedError(
                    "Unhandled result from "
                    "WaitForSingleObject(): %r" % wait_result)

        return False

    finally:
        CloseHandle(hProcess)


def GetExitCodeProcess(hProcess):
    """
    Retrieves the exit code of the given process handle.  To retrieve
    a process handle use :func:`OpenProcess`.

    .. warning::

        You may want to use :func:`process_exit_code` instead of this
        function if you're just checking to see if a process has
        exited at all.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms683189

    :param pywincffi.wintypes.HANDLE hProcess:
        The handle of the process to retrieve the exit code for.

    :returns:
        Returns the exit code of the requested process if one
        can be found.
    """
    input_check("hProcess", hProcess, HANDLE)

    ffi, library = dist.load()
    lpExitCode = ffi.new("LPDWORD")
    code = library.GetExitCodeProcess(wintype_to_cdata(hProcess), lpExitCode)
    error_check("GetExitCodeProcess", code=code, expected=Enums.NON_ZERO)
    return lpExitCode[0]


def OpenProcess(dwDesiredAccess, bInheritHandle, dwProcessId):
    """
    Opens an existing local process object.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms684320

    :param int dwDesiredAccess:
        The required access to the process object.

    :param bool bInheritHandle:
        Enables or disable handle inheritance for child processes.

    :param int dwProcessId:
        The id of the local process to be opened.

    :returns:
        Returns a :class:`pywincffi.wintypes.HANDLE` to the opened process.
        This value can be used by other functions such as
        :func:`TerminateProcess`.
    """
    input_check("dwDesiredAccess", dwDesiredAccess, integer_types)
    input_check("bInheritHandle", bInheritHandle, bool)
    input_check("dwProcessId", dwProcessId, integer_types)
    ffi, library = dist.load()

    handle = library.OpenProcess(
        ffi.cast("DWORD", dwDesiredAccess),
        ffi.cast("BOOL", bInheritHandle),
        ffi.cast("DWORD", dwProcessId)
    )
    error_check("OpenProcess")
    return HANDLE(handle)


def GetCurrentProcess():
    """
    Returns a handle to the current thread.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms683179

    .. note::

        Calling :func:`pywincffi.kernel32.handle.CloseHandle` on the handle
        produced by this function will produce an exception.

    :returns:
        The :class:`pywincffi.wintypes.HANDLE` to the current process.
    """
    _, library = dist.load()
    return HANDLE(library.GetCurrentProcess())


def GetProcessId(Process):  # pylint: disable=invalid-name
    """
    Returns the pid of the process handle provided in ``Process``.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms683215

    :param pywincffi.wintypes.HANDLE Process:
        The handle of the process.

    :return:
        Returns an integer which represents the pid of the given
        process handle.
    """
    input_check("Process", Process, HANDLE)
    _, library = dist.load()
    pid = library.GetProcessId(wintype_to_cdata(Process))
    error_check("GetProcessId")
    return pid


def TerminateProcess(hProcess, uExitCode):
    """
    Terminates the specified process and all of its threads.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms686714

    :param pywincffi.wintypes.HANDLE hProcess:
        A handle to the process to be terminated.

    :param int uExitCode:
        The exit code of the processes and threads as a result of calling
        this function.
    """
    input_check("hProcess", hProcess, HANDLE)
    input_check("uExitCode", uExitCode, integer_types)
    ffi, library = dist.load()
    code = library.TerminateProcess(
        wintype_to_cdata(hProcess),
        ffi.cast("UINT", uExitCode)
    )
    error_check("TerminateProcess", code=code, expected=Enums.NON_ZERO)


def CreateToolhelp32Snapshot(dwFlags, th32ProcessID):
    """
    Takes a snapshot of the specified processes, as well as the heaps,
    modules, and threads used by these processes.

    .. seealso::

        https://msdn.microsoft.com/en-us/ms682489

    :param int dwFlags:
        The portions of the system to be included in the snapshot.

    :param int th32ProcessID:
        The process identifier of the process to be included in the snapshot.

    :rtype: :class:`pywincffi.wintypes.HANDLE`

    :return:
        If the function succeeds,
        it returns an open handle to the specified snapshot.
    """
    input_check("dwFlags", dwFlags, integer_types)
    input_check("th32ProcessID", th32ProcessID, integer_types)
    ffi, library = dist.load()
    process_list = library.CreateToolhelp32Snapshot(
        ffi.cast("DWORD", dwFlags),
        ffi.cast("DWORD", th32ProcessID)
    )

    if process_list == library.INVALID_HANDLE_VALUE:  # pragma: no cover
        raise WindowsAPIError(
            "CreateToolhelp32Snapshot", "Invalid Handle",
            library.INVALID_HANDLE_VALUE,
            expected_return_code="not %r" % library.INVALID_HANDLE_VALUE)

    error_check("CreateToolhelp32Snapshot")

    return HANDLE(process_list)
