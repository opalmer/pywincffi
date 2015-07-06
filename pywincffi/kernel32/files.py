"""
Files
-----

A module containing common Windows file functions.
"""

from six import PY2
from pywincffi.core.ffi import Library, NoneType, input_check, ffi, error_check

kernel32 = Library.load("kernel32")


def CreatePipe(nSize=0, lpPipeAttributes=None):
    """
    Creates an anonymous pipe and returns the read and write handles.

    >>> from pywincffi.core.ffi import ffi
    >>> lpPipeAttributes = ffi.new(
    ...     "SECURITY_ATTRIBUTES[1]", [{
    ...     "nLength": ffi.sizeof("SECURITY_ATTRIBUTES"),
    ...     "bInheritHandle": True,
    ...     "lpSecurityDescriptor": ffi.NULL
    ...     }]
    ... )
    >>> reader, writer = CreatePipe(lpPipeAttributes=lpPipeAttributes)

    :keyword int nSize:
        The size of the buffer in bytes.  Passing in 0, which is the default
        will cause the system to use the default buffer size.

    :keyword lpPipeAttributes:
        The security attributes to apply to the handle. By default
        ``NULL`` will be passed in meaning then handle we create
        cannot be inherited.  For more detailed information see the links
        below.

    :return:
        Returns a tuple of handles containing the reader and writer
        ends of the pipe that was created.  The user of this function
        is responsible for calling CloseHandle at some point.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/windows/desktop/aa365152
        https://msdn.microsoft.com/en-us/library/windows/desktop/aa379560
    """
    input_check("nSize", nSize, int)
    input_check("lpPipeAttributes", lpPipeAttributes, (NoneType, dict))

    hReadPipe = ffi.new("PHANDLE")
    hWritePipe = ffi.new("PHANDLE")

    if lpPipeAttributes is None:
        lpPipeAttributes = ffi.NULL

    code = kernel32.CreatePipe(hReadPipe, hWritePipe, lpPipeAttributes, nSize)
    error_check("CreatePipe", code=code, nonzero=True)

    return hReadPipe[0], hWritePipe[0]


def CloseHandle(hObject):
    """
    Closes an open object handle.

    :param handle hObject:
        The handle object to close.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/windows/desktop/ms724211
    """
    input_check("hObject", hObject, "handle")

    code = kernel32.CloseHandle(hObject)
    error_check("CloseHandle", code=code, nonzero=True)


def WriteFile(hFile, lpBuffer, lpOverlapped=None):
    """
    Writes data to ``hFile`` which may be an I/O device for file.

    :param handle hFile:
        The handle to write to

    :type lpBuffer: bytes, string or unicode.
    :param lpBuffer:
        The data to be written to the file or device. This be data should
        be bytes or a string.

    :returns:
        Returns the number of bytes written

    .. seealso::

        https://msdn.microsoft.com/en-us/library/windows/desktop/aa365747
    """
    if lpOverlapped is None:
        lpOverlapped = ffi.NULL

    if PY2 and not isinstance(lpBuffer, str):
        lpBuffer = unicode(lpBuffer)

    # Prepare string and outputs
    nNumberOfBytesToWrite = len(lpBuffer)
    lpBuffer = ffi.new("wchar_t[%d]" % nNumberOfBytesToWrite, lpBuffer)
    bytes_written = ffi.new("LPDWORD")

    code = kernel32.WriteFile(
        hFile, lpBuffer, ffi.sizeof(lpBuffer), bytes_written, lpOverlapped)
    error_check("WriteFile", code=code, nonzero=True)

    return bytes_written[0]


# TODO: docs and implementation
def ReadFile(hFile, lpBuffer, nNumberOfBytesToWrite, lpOverlapped=None):
    """
    .. seealso::

        https://msdn.microsoft.com/en-us/library/windows/desktop/aa365467

    """
