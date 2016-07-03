"""
Handles
-------

A module containing general functions for working with handle
objects.  The functions provided here are part of the ``kernel32`` library.
"""

from six import integer_types

from pywincffi.core import dist
from pywincffi.core.checks import Enums, input_check, error_check
from pywincffi.exceptions import WindowsAPIError
from pywincffi.wintypes import HANDLE, SOCKET, wintype_to_cdata


def GetStdHandle(nStdHandle):
    """
    Retrieves a handle to the specified standard
    device (standard input, standard output, or standard error).

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms683231

    :param int nStdHandle:
        The standard device to retrieve.

    :rtype: pywincffi.wintypes.HANDLE
    :return:
        Returns a handle to the standard device retrieved.
    """
    _, library = dist.load()
    input_check("nStdHandle", nStdHandle,
                allowed_values=(library.STD_INPUT_HANDLE,
                                library.STD_OUTPUT_HANDLE,
                                library.STD_ERROR_HANDLE))

    handle = library.GetStdHandle(nStdHandle)

    if handle == library.INVALID_HANDLE_VALUE:  # pragma: no cover
        raise WindowsAPIError(
            "GetStdHandle", "Invalid Handle", library.INVALID_HANDLE_VALUE,
            expected_return_code="not %r" % library.INVALID_HANDLE_VALUE)

    return HANDLE(handle)


def CloseHandle(hObject):
    """
    Closes an open object handle.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms724211

    :type hObject: pywincffi.wintypes.HANDLE or pywincffi.wintypes.SOCKET
    :param hObject:
        The handle object to close.
    """
    input_check("hObject", hObject, (HANDLE, SOCKET))
    _, library = dist.load()

    code = library.CloseHandle(wintype_to_cdata(hObject))
    error_check("CloseHandle", code=code, expected=Enums.NON_ZERO)


def GetHandleInformation(hObject):
    """
    Returns properties of an object handle.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms724329

    :param pywincffi.wintypes.HANDLE hObject:
        A handle to an object whose information is to be retrieved.

    :rtype: int
    :return:
        Returns the set of bit flags that specify properties of ``hObject``.
    """
    input_check("hObject", hObject, HANDLE)
    ffi, library = dist.load()

    lpdwFlags = ffi.new("LPDWORD")
    code = library.GetHandleInformation(wintype_to_cdata(hObject), lpdwFlags)
    error_check("GetHandleInformation", code=code, expected=Enums.NON_ZERO)

    return lpdwFlags[0]


def SetHandleInformation(hObject, dwMask, dwFlags):
    """
    Sets properties of an object handle.

    .. seealso::

        https://msdn.microsoft.com/en-us/ms724935

    :param pywincffi.wintypes.HANDLE hObject:
        A handle to an object whose information is to be set.

    :param int dwMask:
        A mask that specifies the bit flags to be changed.

    :param int dwFlags:
        Set of bit flags that specifies properties of ``hObject``.
    """
    input_check("hObject", hObject, HANDLE)
    input_check("dwMask", dwMask, integer_types)
    input_check("dwFlags", dwFlags, integer_types)
    ffi, library = dist.load()

    code = library.SetHandleInformation(
        wintype_to_cdata(hObject),
        ffi.cast("DWORD", dwMask),
        ffi.cast("DWORD", dwFlags)
    )
    error_check("SetHandleInformation", code=code, expected=Enums.NON_ZERO)


def DuplicateHandle(  # pylint: disable=too-many-arguments
        hSourceProcessHandle, hSourceHandle, hTargetProcessHandle,
        dwDesiredAccess, bInheritHandle, dwOptions):
    """
    Duplicates an object handle.

    .. seealso::

        https://msdn.microsoft.com/en-us/ms724251

    :param pywincffi.wintypes.HANDLE hSourceProcessHandle:
        A handle to the process which owns the handle to be duplicated.

    :param pywincffi.wintypes.HANDLE hSourceHandle:
        The handle to be duplicated.

    :param pywincffi.wintypes.HANDLE hTargetProcessHandle:
        A handle to the process which should receive the duplicated handle.

    :param int dwDesiredAccess:
        The access requested for the new handle.

    :param bool bInheritHandle:
        True if the handle should be inheritable by new processes.

    :param int dwOptions:
        Options which control how the handle is duplicated.  Valid
        values are any of the below (or a combination of):

            * ``DUPLICATE_CLOSE_SOURCE`` - Closes the source handle, even
               if there's an error.
            * ``DUPLICATE_SAME_ACCESS`` - Ignores the ``dwDesiredAccess``
               parameter duplicates with the same access as the original
               handle.

    :rtype: pywincffi.wintypes.HANDLE
    :return:
        Returns the duplicated handle.
    """
    ffi, library = dist.load()
    input_check("hSourceProcessHandle", hSourceProcessHandle, HANDLE)
    input_check("hSourceHandle", hSourceHandle, HANDLE)
    input_check("hTargetProcessHandle", hTargetProcessHandle, HANDLE)
    input_check("dwDesiredAccess", dwDesiredAccess, integer_types)
    input_check("bInheritHandle", bInheritHandle, bool)
    input_check("dwOptions", dwOptions, allowed_values=(
        library.DUPLICATE_CLOSE_SOURCE, library.DUPLICATE_SAME_ACCESS,
        library.DUPLICATE_CLOSE_SOURCE | library.DUPLICATE_SAME_ACCESS
    ))

    lpTargetHandle = ffi.new("LPHANDLE")
    code = library.DuplicateHandle(
        wintype_to_cdata(hSourceProcessHandle),
        wintype_to_cdata(hSourceHandle),
        wintype_to_cdata(hTargetProcessHandle),
        lpTargetHandle,
        ffi.cast("DWORD", dwDesiredAccess),
        ffi.cast("BOOL", bInheritHandle),
        ffi.cast("DWORD", dwOptions)
    )
    error_check("DuplicateHandle", code, expected=Enums.NON_ZERO)
    return HANDLE(lpTargetHandle[0])
