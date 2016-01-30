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

import six

from pywincffi.core import dist
from pywincffi.core.checks import Enums, input_check, error_check
from pywincffi.exceptions import WindowsAPIError
from pywincffi.kernel32 import CloseHandle

RESERVED_PIDS = set([0, 4])


def pid_exists(pid):
    """
    Returns True if there's a process associated with ``pid``.

    :param int pid:
        The id of the process to check for.

    :raises ValidationError:
        Raised if there's a problem with the value provided for ``pid``.
    """
    input_check("pid", pid, six.integer_types)

    # Process IDs which always exist shouldn't need to continue
    # further.
    if pid in RESERVED_PIDS:
        return True

    _, library = dist.load()

    try:
        handle = OpenProcess(
            library.PROCESS_QUERY_INFORMATION, False, pid)

    except WindowsAPIError as error:
        # If we can't access the process then it must exist
        # otherwise there would be nothing to access.
        if error.code == library.ERROR_ACCESS_DENIED:
            return True

        if error.code == library.ERROR_INVALID_PARAMETER:
            return False

        raise
    else:
        pass

    CloseHandle(handle)


# TODO: add doc string
def exit_code(pid_or_handle):
    handle = pid_or_handle
    _, library = dist.load()

    if isinstance(pid_or_handle, six.integer_types):
        handle = OpenProcess(
            library.PROCESS_QUERY_INFORMATION, False, pid_or_handle)

    CloseHandle(handle)


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

    :param handle hProcess:
        The handle of the process to retrieve the exit code for

    :returns:
        Returns the exit code of the requested process if one
        can be found.
    """
    input_check("hProcess", hProcess, Enums.HANDLE)

    ffi, library = dist.load()
    lpExitCode = ffi.new("LPDWORD")
    code = library.GetExitCodeProcess(hProcess, lpExitCode)
    error_check("GetExitCodeProcess", code=code, expected=Enums.NON_ZERO)


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
        Returns a handle to the opened process in the form of
        a void pointer.  This value can be used by other functions
        such as :func:`TerminateProcess`
    """
    input_check("dwDesiredAccess", dwDesiredAccess, six.integer_types)
    input_check("bInheritHandle", bInheritHandle, bool)
    input_check("dwProcessId", dwProcessId, six.integer_types)
    ffi, library = dist.load()

    handle = library.OpenProcess(
        ffi.cast("DWORD", dwDesiredAccess),
        ffi.cast("BOOL", bInheritHandle),
        ffi.cast("DWORD", dwProcessId)
    )
    error_check("OpenProcess")
    return handle


def GetCurrentProcess():
    """
    Returns a handle to the current thread.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms683179

    .. note::

        Calling :func:`pywincffi.kernel32.handle.CloseHandle` on the handle
        produced by this function will produce an exception.

    :returns:
        The handle to the current process.
    """
    _, library = dist.load()
    return library.GetCurrentProcess()


def GetProcessId(Process):  # pylint: disable=invalid-name
    """
    Returns the pid of the process handle provided in ``Process``.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms683215

    :param handle Process:
        The handle of the process to re

    :return:
        Returns an integer which represents the pid of the given
        process handle.
    """
    input_check("Process", Process, Enums.HANDLE)
    _, library = dist.load()
    pid = library.GetProcessId(Process)
    error_check("GetProcessId")
    return pid


#
# if __name__ == "__main__":
#     import os
#     import subprocess
#     import sys
#
#     # process = subprocess.Popen(
#     #     [sys.executable, "-c", "import time; time.sleep(3)"])
#     # pid = process.pid
#     pid = os.getpid()
#
#     ffi, library = dist.load()
#     handle = OpenProcess(
#         library.PROCESS_QUERY_INFORMATION, True, pid)
#     print(handle)
#     # process.communicate()
#     # print(GetExitCodeProcess(handle))
