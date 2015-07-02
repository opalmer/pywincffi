"""
Kernel32
========

Provides functions, constants and utilities that wrap the Windows
kernel32 library.  This module also provides several constants as well, see
Microsoft's documentation for the constant names and their purpose:

    * **Process Security and Access Rights** -
      https://msdn.microsoft.com/en-us/library/windows/desktop/ms684880

.. note::

    Not all constants may be defined
"""

import six
from pywincffi.core.ffi import bind, ffi, input_check, error_check

_kernel32 = bind(ffi, "kernel32")

PROCESS_CREATE_PROCESS = 0x0080
PROCESS_CREATE_THREAD = 0x0002
PROCESS_DUP_HANDLE = 0x0040
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
PROCESS_SET_INFORMATION = 0x0200
PROCESS_SET_QUOTA = 0x0100
PROCESS_SUSPEND_RESUME = 0x0800
PROCESS_TERMINATE = 0x0001
PROCESS_VM_OPERATION = 0x0008
PROCESS_VM_READ = 0x0008
PROCESS_VM_WRITE = 0x0020
SYNCHRONIZE = 0x00100000


def SetLastError(dwErrCode):
    """
    Sets the last error code using the Windows API.  This function
    generally should only be used by tests.

    :param int dwErrCode:
        The error code to set
    """
    input_check("dwErrCode", dwErrCode, six.integer_types)
    _kernel32.SetLastError(ffi.cast("DWORD", dwErrCode))


def OpenProcess(dwDesiredAccess, bInheritHandle, dwProcessId):
    """
    Opens an existing local process object.

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

    .. seealso::

        https://msdn.microsoft.com/en-us/library/windows/desktop/ms684320
    """
    input_check("dwDesiredAccess", dwDesiredAccess, six.integer_types)
    input_check("bInheritHandle", bInheritHandle, bool)
    input_check("dwProcessId", dwProcessId, six.integer_types)

    handle_id = _kernel32.OpenProcess(
        ffi.cast("DWORD", dwDesiredAccess),
        ffi.cast("BOOL", bInheritHandle),
        ffi.cast("DWORD", dwProcessId)
    )
    error_check("OpenProcess")

    return ffi.new_handle(handle_id)


def TerminateProcess(hProcess, uExitCode):
    """
    Terminates the given process as declared by the handle provided
    by ``hProcess``.  For example::

    >>> import os
    >>> from pywincffi.kernel32 import (
    ...     PROCESS_TERMINATE, OpenProcess, TerminateProcess)
    >>> handle = OpenProcess(PROCESS_TERMINATE, False, os.getpid())
    >>> TerminateProcess(handle, 0)

    :param handle hProcess:
        A handle to the process to terminate.  Functions such as
        :func:`OpenProcess` return a handle that can be used here.

    :param int uExitCode:
       The exit code to terminate the process with.
    """
    input_check("hProcess", hProcess, "handle")
    input_check("uExitCode", uExitCode, six.integer_types)

    code = _kernel32.TerminateProcess(
        hProcess,
        uExitCode
    )
    error_check("TerminateProcess", code=code, nonzero=True)

if __name__ == "__main__":
    import os
    handle = OpenProcess(PROCESS_TERMINATE, False, os.getpid())
    TerminateProcess(handle, 1)
