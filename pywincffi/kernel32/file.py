"""
Files
-----

A module containing common Windows file functions for working with files.
"""

from six import PY3, PY2, integer_types, string_types

from pywincffi.core import dist
from pywincffi.core.checks import Enums, input_check, error_check
from pywincffi.util import string_to_cdata


def WriteFile(hFile, lpBuffer, nNumberOfBytesToWrite=None, lpOverlapped=None,
              lpBufferType="wchar_t[]"):
    """
    Writes data to ``hFile`` which may be an I/O device for file.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/aa365747

    :param handle hFile:
        The handle to write to

    :type lpBuffer: bytes, string or unicode.
    :param lpBuffer:
        The data to be written to the file or device. We should be able
        to convert this value to unicode.

    :keyword int nNumberOfBytesToWrite:
        The number of bytes to be written.  By default this will
        be determinted based on the size of ``lpBuffer``

    :type lpOverlapped: None or OVERLAPPED
    :keyword lpOverlapped:
        None or a pointer to a ``OVERLAPPED`` structure.  See Microsoft's
        documentation for intended usage and below for an example of this
        struct.

        >>> from pywincffi.core import dist
        >>> from pywincffi.kernel32 import WriteFile
        >>> ffi, library = dist.load()
        >>> hFile = None # normally, this would be a handle
        >>> lpOverlapped = ffi.new(
        ...     "OVERLAPPED[1]", [{
        ...         "hEvent": hFile
        ...     }]
        ... )
        >>> bytes_written = WriteFile(
        ...     hFile, "Hello world", lpOverlapped=lpOverlapped)

    :keyword str lpBufferType:
        The type which should be passed to :meth:`ffi.new`.  If the data
        you're passing into this function is a string and you're using Python
        2 for example you might use ``char[]`` here instead.

    :returns:
        Returns the number of bytes written
    """
    ffi, library = dist.load()

    if lpOverlapped is None:
        lpOverlapped = ffi.NULL

    input_check("hFile", hFile, Enums.HANDLE)
    input_check("lpBuffer", lpBuffer, string_types)
    input_check("lpOverlapped", lpOverlapped, Enums.OVERLAPPED)
    input_check(
        "lpBufferType", lpBufferType, allowed_values=("char[]", "wchar_t[]"))

    lpBuffer = ffi.new(lpBufferType, lpBuffer)

    if nNumberOfBytesToWrite is None:
        nNumberOfBytesToWrite = ffi.sizeof(lpBuffer)

    input_check("nNumberOfBytesToWrite", nNumberOfBytesToWrite, integer_types)

    bytes_written = ffi.new("LPDWORD")
    code = library.WriteFile(
        hFile, lpBuffer, nNumberOfBytesToWrite, bytes_written, lpOverlapped)
    error_check("WriteFile", code=code, expected=Enums.NON_ZERO)

    return bytes_written[0]


def ReadFile(hFile, nNumberOfBytesToRead, lpOverlapped=None):
    """
    Read the specified number of bytes from ``hFile``.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/aa365467

    :param handle hFile:
        The handle to read from

    :param int nNumberOfBytesToRead:
        The number of bytes to read from ``hFile``

    :type lpOverlapped: None or OVERLAPPED
    :keyword lpOverlapped:
        None or a pointer to a ``OVERLAPPED`` structure.  See Microsoft's
        documentation for intended usage and below for an example of this
        struct.

        >>> from pywincffi.core import dist
        >>> ffi, library = dist.load()
        >>> hFile = None # normally, this would be a handle
        >>> lpOverlapped = ffi.new(
        ...     "OVERLAPPED[1]", [{
        ...         "hEvent": hFile
        ...     }]
        ... )
        >>> read_data = ReadFile(  # read 12 bytes from hFile
        ...     hFile, 12, lpOverlapped=lpOverlapped)

    :returns:
        Returns the data read from ``hFile``
    """
    ffi, library = dist.load()

    if lpOverlapped is None:
        lpOverlapped = ffi.NULL

    input_check("hFile", hFile, Enums.HANDLE)
    input_check("nNumberOfBytesToRead", nNumberOfBytesToRead, integer_types)
    input_check("lpOverlapped", lpOverlapped, Enums.OVERLAPPED)

    lpBuffer = ffi.new("wchar_t[%d]" % nNumberOfBytesToRead)
    bytes_read = ffi.new("LPDWORD")
    code = library.ReadFile(
        hFile, lpBuffer, ffi.sizeof(lpBuffer), bytes_read, lpOverlapped
    )
    error_check("ReadFile", code=code, expected=Enums.NON_ZERO)
    return ffi.string(lpBuffer)


def MoveFileEx(lpExistingFileName, lpNewFileName, dwFlags=None):
    """
    Moves an existing file or directory, including its children,
    see the MSDN documentation for full options.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/aa365240

    :param str lpExistingFileName:
        Name of the file or directory to perform the operation on.

    :param str lpNewFileName:
        Optional new name of the path or directory.  This value may be
        ``None``.

    :keyword int dwFlags:
        Parameters which control the operation of :func:`MoveFileEx`.  See
        the MSDN documentation for full details.  By default
        ``MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH`` is used.
    """
    ffi, library = dist.load()

    if dwFlags is None:
        dwFlags = \
            library.MOVEFILE_REPLACE_EXISTING | library.MOVEFILE_WRITE_THROUGH

    input_check("lpExistingFileName", lpExistingFileName, string_types)
    input_check("dwFlags", dwFlags, integer_types)

    if lpNewFileName is not None:
        input_check("lpNewFileName", lpNewFileName, string_types)
        lpNewFileName = string_to_cdata(lpNewFileName)
    else:
        lpNewFileName = ffi.NULL

    code = library.MoveFileEx(
        string_to_cdata(lpExistingFileName),
        lpNewFileName,
        ffi.cast("DWORD", dwFlags)
    )
    error_check("MoveFileEx", code=code, expected=Enums.NON_ZERO)
