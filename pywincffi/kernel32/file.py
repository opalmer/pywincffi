"""
Files
-----

A module containing common Windows file functions for working with files.
"""

from six import PY3, integer_types, string_types

from pywincffi.core import dist
from pywincffi.core.checks import Enums, input_check, error_check
from pywincffi.exceptions import WindowsAPIError
from pywincffi.util import string_to_cdata


def CreateFile(  # pylint: disable=too-many-arguments
        lpFileName, dwDesiredAccess, dwShareMode=None,
        lpSecurityAttributes=None, dwCreationDisposition=None,
        dwFlagsAndAttributes=None, hTemplateFile=None):
    """
    Creates or opens a file or other I/O device.  Default values are
    provided for some of the default arguments for CreateFile() so
    its behavior is close to Pythons :func:`open` function.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/aa363858
        https://msdn.microsoft.com/en-us/library/gg258116

    :param str lpFileName:
        The path to the file or device being created or opened.

    :param int dwDesiredAccess:
        The requested access to the file or device.  Microsoft's documentation
        has extensive notes on this parameter in the seealso links above.

    :keyword int dwShareMode:
        Access and sharing rights to the handle being created.  If not provided
        with an explicit value, ``FILE_SHARE_READ`` will be used which will
        other open operations or process to continue to read from the file.

    :keyword struct lpSecurityAttributes:
        A pointer to a ``SECURITY_ATTRIBUTES`` structure, see Microsoft's
        documentation for more detailed information.  If not provided with
        an explicit value, NULL will be used instead which will mean the
        handle can't be inherited by any child process.

    :keyword int dwCreationDisposition:
        Action to take when the file or device does not exist.  If not
        provided with an explicit value, ``CREATE_ALWAYS`` will be used
        which means existing files will be overwritten.

    :keyword int dwFlagsAndAttributes:
        The file or device attributes and flags.  If not provided an explict
        value, ``FILE_ATTRIBUTE_NORMAL`` will be used giving the handle
        essentially no special attributes.

    :keyword handle hTemplateFile:
        A value handle to a template file with the ``GENERIC_READ`` access
        right.  See Microsoft's documentation for more information.  If not
        provided an explicit value, ``NULL`` will be used instead.

    :return:
        Returns the file handle created by ``CreateFile``.
    """
    ffi, library = dist.load()

    if dwShareMode is None:
        dwShareMode = library.FILE_SHARE_READ

    if lpSecurityAttributes is None:
        lpSecurityAttributes = ffi.NULL

    if dwCreationDisposition is None:
        dwCreationDisposition = library.CREATE_ALWAYS

    if dwFlagsAndAttributes is None:
        dwFlagsAndAttributes = library.FILE_ATTRIBUTE_NORMAL

    if hTemplateFile is None:
        hTemplateFile = ffi.NULL

    input_check("lpFileName", lpFileName, string_types)
    input_check("dwDesiredAccess", dwDesiredAccess, integer_types)
    input_check("dwShareMode", dwShareMode, integer_types)
    input_check(
        "lpSecurityAttributes", lpSecurityAttributes,
        Enums.SECURITY_ATTRIBUTES
    )
    input_check(
        "dwCreationDisposition", dwCreationDisposition,
        allowed_values=(
            library.CREATE_ALWAYS,
            library.CREATE_NEW,
            library.OPEN_ALWAYS,
            library.OPEN_EXISTING,
            library.TRUNCATE_EXISTING
        )
    )
    input_check("dwFlagsAndAttributes", dwFlagsAndAttributes, integer_types)
    input_check("hTemplateFile", hTemplateFile, Enums.HANDLE)

    handle = library.CreateFile(
        string_to_cdata(lpFileName), dwDesiredAccess, dwShareMode,
        lpSecurityAttributes, dwCreationDisposition, dwFlagsAndAttributes,
        hTemplateFile
    )

    try:
        error_check("CreateFile")
    except WindowsAPIError as error:
        # ERROR_ALREADY_EXISTS may be a normal condition depending
        # on the creation disposition.
        if (dwCreationDisposition == library.CREATE_ALWAYS and
                error.errno == library.ERROR_ALREADY_EXISTS):
            return handle
        raise

    return handle


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

    lpBufferTypes = string_types
    if PY3:
        lpBufferTypes = tuple(list(string_types) + [bytes])

    input_check("hFile", hFile, Enums.HANDLE)
    input_check("lpBuffer", lpBuffer, lpBufferTypes)
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


def FlushFileBuffers(hFile):
    """
    Flushes the buffer of the specified file to disk.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/aa364439

    :param handle hFile:
        The handle to flush to disk.
    """
    input_check("hFile", hFile, Enums.HANDLE)
    _, library = dist.load()
    code = library.FlushFileBuffers(hFile)
    error_check("FlushFileBuffers", code=code, expected=Enums.NON_ZERO)


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


def LockFileEx(
        hFile, dwFlags, nNumberOfBytesToLockLow, nNumberOfBytesToLockHigh,
        lpOverlapped=None):
    """
    Locks ``hFile`` for exclusive access by the calling process.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/aa365203

    :param handle hFile:
        The handle to the file to lock.  This handle must have been
        created with either the ``GENERIC_READ`` or ``GENERIC_WRITE``
        right.

    :param int dwFlags:
        One or more of the following flags:

            * ``LOCKFILE_EXCLUSIVE_LOCK`` - Request an exclusive lock.
            * ``LOCKFILE_FAIL_IMMEDIATELY`` - Return immediately if the lock
              could not be acquired.  Otherwise :func:`LockFileEx` will wait.

    :param int nNumberOfBytesToLockLow:
        The start of the byte range to lock.

    :param int nNumberOfBytesToLockHigh:
        The end of the byte range to lock.

    :keyword LPOVERLAPPED lpOverlapped:
        A pointer to an ``OVERLAPPED`` structure.  If not provided
        one will be constructed for you.
    """
    input_check("hFile", hFile, Enums.HANDLE)
    input_check("dwFlags", dwFlags, integer_types)
    input_check(
        "nNumberOfBytesToLockLow", nNumberOfBytesToLockLow, integer_types)
    input_check(
        "nNumberOfBytesToLockHigh", nNumberOfBytesToLockHigh, integer_types)

    ffi, library = dist.load()

    if lpOverlapped is None:
        lpOverlapped = ffi.new("OVERLAPPED[]", [{"hEvent": hFile}])

    input_check("lpOverlapped", lpOverlapped, Enums.OVERLAPPED)

    code = library.LockFileEx(
        hFile,
        ffi.cast("DWORD", dwFlags),
        ffi.cast("DWORD", 0),  # "_Reserveved_"
        ffi.cast("DWORD", nNumberOfBytesToLockLow),
        ffi.cast("DWORD", nNumberOfBytesToLockHigh),
        lpOverlapped
    )
    error_check("LockFileEx", code=code, expected=Enums.NON_ZERO)


def UnlockFileEx(
        hFile, nNumberOfBytesToUnlockLow, nNumberOfBytesToUnlockHigh,
        lpOverlapped=None):
    """
    Unlocks a region in the specified file.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/aa365716

    :param handle hFile:
        The handle to the file to unlock.  This handle must have been
        created with either the ``GENERIC_READ`` or ``GENERIC_WRITE``
        right.

    :param int nNumberOfBytesToUnlockLow:
        The start of the byte range to unlock.

    :param int nNumberOfBytesToUnlockHigh:
        The end of the byte range to unlock.

    :keyword LPOVERLAPPED lpOverlapped:
        A pointer to an ``OVERLAPPED`` structure.  If not provided
        one will be constructed for you.
    """
    input_check("hFile", hFile, Enums.HANDLE)
    input_check(
        "nNumberOfBytesToUnlockLow",
        nNumberOfBytesToUnlockLow, integer_types)
    input_check(
        "nNumberOfBytesToUnlockHigh",
        nNumberOfBytesToUnlockHigh, integer_types)

    ffi, library = dist.load()

    if lpOverlapped is None:
        lpOverlapped = ffi.new("OVERLAPPED[]", [{"hEvent": hFile}])

    input_check("lpOverlapped", lpOverlapped, Enums.OVERLAPPED)

    code = library.UnlockFileEx(
        hFile,
        ffi.cast("DWORD", 0),  # "_Reserveved_"
        ffi.cast("DWORD", nNumberOfBytesToUnlockLow),
        ffi.cast("DWORD", nNumberOfBytesToUnlockHigh),
        lpOverlapped
    )
    error_check("UnlockFileEx", code=code, expected=Enums.NON_ZERO)
