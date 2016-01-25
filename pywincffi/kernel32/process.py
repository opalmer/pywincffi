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
from pywincffi.core.checks import input_check, error_check


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

    handle_id = library.OpenProcess(
        ffi.cast("DWORD", dwDesiredAccess),
        ffi.cast("BOOL", bInheritHandle),
        ffi.cast("DWORD", dwProcessId)
    )
    error_check("OpenProcess")

    return ffi.new_handle(handle_id)


def GetCurrentProcess():
    """
    Returns a handle to the current thread.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms683179

    .. note::

        Calling :func:`pywincffi.kernel32.io.CloseHandle` on the handle
        produced by this function will produce an exception.

    :returns:
        The handle to the current process.
    """
    _, library = dist.load()
    return library.GetCurrentProcess()
