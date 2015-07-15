"""
Files
-----

A module containing common Windows file functions.
"""

from six import integer_types

from pywincffi.core.ffi import Library, ffi
from pywincffi.core.checks import Enums, input_check, error_check, NoneType

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
    error_check("CreatePipe", code=code, expected=Enums.NON_ZERO)

    return hReadPipe[0], hWritePipe[0]


def CloseHandle(hObject):
    """
    Closes an open object handle.

    :param handle hObject:
        The handle object to close.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/windows/desktop/ms724211
    """
    input_check("hObject", hObject, Enums.HANDLE)

    code = kernel32.CloseHandle(hObject)
    error_check("CloseHandle", code=code, expected=Enums.NON_ZERO)


def WriteFile(hFile, lpBuffer, lpOverlapped=None):
    """
    Writes data to ``hFile`` which may be an I/O device for file.

    :param handle hFile:
        The handle to write to

    :type lpBuffer: bytes, string or unicode.
    :param lpBuffer:
        The data to be written to the file or device. We should be able
        to convert this value to unicode.

    :type lpOverlapped: None or OVERLAPPED
    :param lpOverlapped:
        None or a pointer to a ``OVERLAPPED`` structure.  See Microsoft's
        documentation for intended usage and below for an example of this
        struct.

        >>> from pywincffi.core.ffi import ffi
        >>> reader = None # normally, this would be a handle
        >>> struct = ffi.new(
        ...     "OVERLAPPED[1]", [{
        ...         "hEvent": reader
        ...     }]
        ... )

    :returns:
        Returns the number of bytes written

    .. seealso::

        https://msdn.microsoft.com/en-us/library/windows/desktop/aa365747
    """
    if lpOverlapped is None:
        lpOverlapped = ffi.NULL

    input_check("hFile", hFile, Enums.HANDLE)
    input_check("lpBuffer", lpBuffer, Enums.UTF8)
    input_check("lpOverlapped", lpOverlapped, Enums.OVERLAPPED)

    # Prepare string and outputs
    nNumberOfBytesToWrite = len(lpBuffer)
    lpBuffer = ffi.new("wchar_t[%d]" % nNumberOfBytesToWrite, lpBuffer)
    bytes_written = ffi.new("LPDWORD")

    code = kernel32.WriteFile(
        hFile, lpBuffer, ffi.sizeof(lpBuffer), bytes_written, lpOverlapped)
    error_check("WriteFile", code=code, expected=Enums.NON_ZERO)

    return bytes_written[0]


def ReadFile(hFile, nNumberOfBytesToRead, lpOverlapped=None):
    """
    :param handle hFile:
        The handle to read from

    :param int nNumberOfBytesToRead:
        The number of bytes to read from ``hFile``

    :type lpOverlapped: None or OVERLAPPED
    :param lpOverlapped:
        None or a pointer to a ``OVERLAPPED`` structure.  See Microsoft's
        documentation for intended usage and below for an example of this
        struct.

        >>> from pywincffi.core.ffi import ffi
        >>> reader = None # normally, this would be a handle
        >>> struct = ffi.new(
        ...     "OVERLAPPED[1]", [{
        ...         "hEvent": reader
        ...     }]
        ... )

    :returns:
        Returns the data read from ``hFile``

    .. seealso::

        https://msdn.microsoft.com/en-us/library/windows/desktop/aa365467

    """
    if lpOverlapped is None:
        lpOverlapped = ffi.NULL

    input_check("hFile", hFile, Enums.HANDLE)
    input_check("nNumberOfBytesToRead", nNumberOfBytesToRead, integer_types)
    input_check("lpOverlapped", lpOverlapped, Enums.OVERLAPPED)

    lpBuffer = ffi.new("wchar_t[%d]" % nNumberOfBytesToRead)
    bytes_read = ffi.new("LPDWORD")
    code = kernel32.ReadFile(
        hFile, lpBuffer, ffi.sizeof(lpBuffer), bytes_read, lpOverlapped
    )
    error_check("ReadFile", code=code, expected=Enums.NON_ZERO)
    return ffi.string(lpBuffer)
