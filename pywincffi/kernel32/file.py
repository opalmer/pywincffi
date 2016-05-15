"""
Files
-----

A module containing common Windows file functions for working with files.
"""

from six import PY3, integer_types, string_types, text_type, binary_type

from pywincffi.core import dist
from pywincffi.core.checks import Enums, input_check, error_check, NoneType
from pywincffi.exceptions import WindowsAPIError
from pywincffi.util import string_to_cdata
from pywincffi.wintypes import (
    SECURITY_ATTRIBUTES, OVERLAPPED, wintype_to_cdata
)


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

    :param unicode/str lpFileName:
        Type is unicode on Python 2, str on Python 3.
        The path to the file or device being created or opened.

    :param int dwDesiredAccess:
        The requested access to the file or device.  Microsoft's documentation
        has extensive notes on this parameter in the seealso links above.

    :keyword int dwShareMode:
        Access and sharing rights to the handle being created.  If not provided
        with an explicit value, ``FILE_SHARE_READ`` will be used which will
        other open operations or process to continue to read from the file.

    :keyword struct lpSecurityAttributes:
        :class:`pywincffi.wintypes.SECURITY_ATTRIBUTES` or None.
        See Microsoft's documentation for more detailed information.

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

    if dwCreationDisposition is None:
        dwCreationDisposition = library.CREATE_ALWAYS

    if dwFlagsAndAttributes is None:
        dwFlagsAndAttributes = library.FILE_ATTRIBUTE_NORMAL

    if hTemplateFile is None:
        hTemplateFile = ffi.NULL

    input_check("lpFileName", lpFileName, text_type)
    input_check("dwDesiredAccess", dwDesiredAccess, integer_types)
    input_check("dwShareMode", dwShareMode, integer_types)
    input_check(
        "lpSecurityAttributes", lpSecurityAttributes,
        allowed_types=(NoneType, SECURITY_ATTRIBUTES)
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
        lpFileName, dwDesiredAccess, dwShareMode,
        wintype_to_cdata(lpSecurityAttributes), dwCreationDisposition,
        dwFlagsAndAttributes, hTemplateFile
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


def WriteFile(hFile, lpBuffer, nNumberOfBytesToWrite=None, lpOverlapped=None):
    """
    Writes data to ``hFile`` which may be an I/O device for file.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/aa365747

    :param handle hFile:
        The handle to write to

    :type lpBuffer: str/bytes
    :param lpBuffer:
        Type is str on Python 2, bytes on Python 3.
        The data to be written to the file or device.

    :keyword int nNumberOfBytesToWrite:
        The number of bytes to be written.  Defaults to len(lpBuffer).

    :type lpOverlapped: None or :class:`pywincffi.wintypes.OVERLAPPED`
    :keyword lpOverlapped:
        See Microsoft's documentation for intended usage and below for
        an example.

        >>> from pywincffi.core import dist
        >>> from pywincffi.kernel32 import WriteFile, CreateEvent
        >>> from pywincffi.wintypes import OVERLAPPED
        >>> hEvent = CreateEvent(...)
        >>> lpOverlapped = OVERLAPPED()
        >>> lpOverlapped.hEvent = hEvent[0]
        >>> bytes_written = WriteFile(
        ...     hFile, "Hello world", lpOverlapped=lpOverlapped)

    :returns:
        Returns the number of bytes written
    """
    ffi, library = dist.load()

    input_check("hFile", hFile, Enums.HANDLE)
    input_check("lpBuffer", lpBuffer, binary_type)
    input_check(
        "lpOverlapped", lpOverlapped,
        allowed_types=(NoneType, OVERLAPPED)
    )

    if nNumberOfBytesToWrite is None:
        nNumberOfBytesToWrite = len(lpBuffer)
    else:
        input_check(
            "nNumberOfBytesToWrite", nNumberOfBytesToWrite,
            integer_types
        )

    bytes_written = ffi.new("LPDWORD")
    code = library.WriteFile(
        hFile, lpBuffer, nNumberOfBytesToWrite, bytes_written,
        wintype_to_cdata(lpOverlapped)
    )
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

    :type lpOverlapped: None or :class:`pywincffi.wintypes.OVERLAPPED`
    :keyword lpOverlapped:
        See Microsoft's documentation for intended usage and below for
        an example.

        >>> from pywincffi.core import dist
        >>> from pywincffi.kernel32 import ReadFile, CreateEvent
        >>> from pywincffi.wintypes import OVERLAPPED
        >>> hEvent = CreateEvent(...)
        >>> lpOverlapped = OVERLAPPED()
        >>> lpOverlapped.hEvent = hEvent[0]
        >>> read_data = ReadFile(  # read 12 bytes from hFile
        ...     hFile, 12, lpOverlapped=lpOverlapped)

    :returns:
        Returns the data read from ``hFile``
    """
    ffi, library = dist.load()

    input_check("hFile", hFile, Enums.HANDLE)
    input_check("nNumberOfBytesToRead", nNumberOfBytesToRead, integer_types)
    input_check(
        "lpOverlapped", lpOverlapped,
        allowed_types=(NoneType, OVERLAPPED)
    )

    lpBuffer = ffi.new("wchar_t[%d]" % nNumberOfBytesToRead)
    bytes_read = ffi.new("LPDWORD")
    code = library.ReadFile(
        hFile, lpBuffer, ffi.sizeof(lpBuffer), bytes_read,
        wintype_to_cdata(lpOverlapped)
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

    :type lpOverlapped: None or :class:`pywincffi.wintypes.OVERLAPPED`
    :keyword lpOverlapped:
        The underlying Windows API requires lpOverlapped, which acts both
        an input argument and may contain results after calling. If None is
        provided, a throw-away zero-filled instance will be created to
        support such call. See Microsoft's documentation for intended usage.
    """
    input_check("hFile", hFile, Enums.HANDLE)
    input_check("dwFlags", dwFlags, integer_types)
    input_check(
        "nNumberOfBytesToLockLow", nNumberOfBytesToLockLow, integer_types)
    input_check(
        "nNumberOfBytesToLockHigh", nNumberOfBytesToLockHigh, integer_types)

    ffi, library = dist.load()

    if lpOverlapped is None:
        # Required by Windows API, create a throw-away zero-filled instance.
        lpOverlapped = OVERLAPPED()
    else:
        input_check("lpOverlapped", lpOverlapped, allowed_types=OVERLAPPED)

    code = library.LockFileEx(
        hFile,
        ffi.cast("DWORD", dwFlags),
        ffi.cast("DWORD", 0),  # "_Reserveved_"
        ffi.cast("DWORD", nNumberOfBytesToLockLow),
        ffi.cast("DWORD", nNumberOfBytesToLockHigh),
        wintype_to_cdata(lpOverlapped)
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

    :type lpOverlapped: None or :class:`pywincffi.wintypes.OVERLAPPED`
    :keyword lpOverlapped:
        The underlying Windows API requires lpOverlapped, which acts both
        an input argument and may contain results after calling. If None is
        provided, a throw-away zero-filled instance will be created to
        support such call. See Microsoft's documentation for intended usage.
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
        # Required by Windows API, create a throw-away zero-filled instance.
        lpOverlapped = OVERLAPPED()
    else:
        input_check("lpOverlapped", lpOverlapped, allowed_types=OVERLAPPED)

    code = library.UnlockFileEx(
        hFile,
        ffi.cast("DWORD", 0),  # "_Reserveved_"
        ffi.cast("DWORD", nNumberOfBytesToUnlockLow),
        ffi.cast("DWORD", nNumberOfBytesToUnlockHigh),
        wintype_to_cdata(lpOverlapped)
    )
    error_check("UnlockFileEx", code=code, expected=Enums.NON_ZERO)
