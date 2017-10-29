"""
Console
-------

A module containing functions for interacting with a Windows
console.
"""

from six import integer_types

from pywincffi.core import dist
from pywincffi.core.checks import NON_ZERO, NoneType, input_check, error_check
from pywincffi.exceptions import WindowsAPIError
from pywincffi.wintypes import HANDLE, SECURITY_ATTRIBUTES, wintype_to_cdata


def SetConsoleTextAttribute(hConsoleOutput, wAttributes):
    """
    Sets the attributes of characters written to a console buffer.

    .. seealso::

        https://docs.microsoft.com/en-us/windows/console/setconsoletextattribute

    :param pywincffi.wintypes.HANDLE hConsoleOutput:
        A handle to the console screen buffer. The handle must have the
        ``GENERIC_READ`` access right.

    :param int wAttributes:
        The character attribute(s) to set.
    """
    input_check("hConsoleOutput", hConsoleOutput, HANDLE)
    input_check("wAttributes", wAttributes, integer_types)
    ffi, library = dist.load()
    # raise Exception(type(wAttributes))
    # info = ffi.new("PCHAR_INFO")
    code = library.SetConsoleTextAttribute(
        wintype_to_cdata(hConsoleOutput),
        ffi.cast("ATOM", wAttributes)
    )
    error_check("SetConsoleTextAttribute", code=code, expected=NON_ZERO)


def GetConsoleScreenBufferInfo(hConsoleOutput):
    """
    Retrieves information about the specified console screen buffer.

    .. seealso::

        https://docs.microsoft.com/en-us/windows/console/getconsolescreenbufferinfo

    :param pywincffi.wintypes.HANDLE hConsoleOutput:
        A handle to the console screen buffer. The handle must have the
        ``GENERIC_READ`` access right.

    :returns:
        Returns a ffi data structure with attributes corresponding to
        the fields on the ``PCONSOLE_SCREEN_BUFFER_INFO`` struct.
    """
    input_check("hConsoleOutput", hConsoleOutput, HANDLE)
    ffi, library = dist.load()
    info = ffi.new("PCONSOLE_SCREEN_BUFFER_INFO")
    code = library.GetConsoleScreenBufferInfo(
        wintype_to_cdata(hConsoleOutput), info)
    error_check("GetConsoleScreenBufferInfo", code, expected=NON_ZERO)
    return info


def CreateConsoleScreenBuffer(
        dwDesiredAccess, dwShareMode, lpSecurityAttributes=None, dwFlags=None):
    """
    Creates a console screen buffer.

    .. seealso::

        https://docs.microsoft.com/en-us/windows/console/createconsolescreenbuffer

    :param int dwDesiredAccess:
         The access to the console screen buffer. If `None` is provided
         then the Windows APIs will use a default security descriptor.

    :type dwShareMode: int or None
    :param dwShareMode:
        Controls the options for sharing the resulting handle. If `None` or
        0 then the resulting buffer cannot be shared.

    :keyword pywincffi.wintypes.SECURITY_ATTRIBUTES lpSecurityAttributes:
        Extra security attributes that determine if the resulting handle
        can be inherited. If `None` is provided, which is the default, then
        the handle cannot be inherited.

    :keyword int dwFlags:
        The type of console buffer to create. The flag is superficial because
        it only accepts None or ``CONSOLE_TEXTMODE_BUFFER`` as inputs. If no
        value is provided, which is the default, then
        ``CONSOLE_TEXTMODE_BUFFER`` is automatically used.

    :rtype: :class:`pywincffi.wintypes.HANDLE``
    :returns:
        Returns the handle created by the underlying C function.
        :func:`pywincffi.kernel32.CloseHandle` should be called on the handle
        when you are done with it.
    """
    ffi, library = dist.load()

    if dwDesiredAccess is None:
        dwDesiredAccess = ffi.NULL

    if dwShareMode is None:
        dwShareMode = 0

    if dwFlags is None:
        dwFlags = library.CONSOLE_TEXTMODE_BUFFER

    input_check(
        "dwDesiredAccess", dwDesiredAccess, allowed_values=(
            ffi.NULL,
            library.GENERIC_READ,
            library.GENERIC_WRITE,
            library.GENERIC_READ | library.GENERIC_WRITE
        ))
    input_check(
        "dwShareMode", dwShareMode, allowed_values=(
            0,
            library.FILE_SHARE_READ,
            library.FILE_SHARE_WRITE,
            library.FILE_SHARE_READ | library.FILE_SHARE_WRITE,
        ))
    input_check(
        "dwFlags", dwFlags,
        allowed_values=(
            library.CONSOLE_TEXTMODE_BUFFER,
        ))
    input_check(
        "lpSecurityAttributes", lpSecurityAttributes,
        allowed_types=(NoneType, SECURITY_ATTRIBUTES))

    if lpSecurityAttributes is None:
        lpSecurityAttributes = ffi.NULL

    handle = library.CreateConsoleScreenBuffer(
        ffi.cast("DWORD", dwDesiredAccess),
        ffi.cast("DWORD", dwShareMode),
        lpSecurityAttributes,
        ffi.cast("DWORD", dwFlags),
        ffi.NULL  # _reserved_
    )

    if handle == library.INVALID_HANDLE_VALUE:  # pragma: no cover
        raise WindowsAPIError(
            "CreateConsoleScreenBuffer", "Invalid Handle",
            library.INVALID_HANDLE_VALUE,
            expected_return_code="not INVALID_HANDLE_VALUE")

    return HANDLE(handle)
