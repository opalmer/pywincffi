"""
Files
-----

A module containing common Windows file functions.
"""

from collections import namedtuple

from six import integer_types

from pywincffi.core.ffi import Library
from pywincffi.core.checks import Enums, input_check, error_check, NoneType
from pywincffi.exceptions import WindowsAPIError

PeekNamedPipeResult = namedtuple(
    "PeekNamedPipeResult",
    ("lpBuffer", "lpBytesRead", "lpTotalBytesAvail",
     "lpBytesLeftThisMessage")
)


def handle_from_file(python_file):
    """
    Given a standard Python file object produce a Windows
    handle object that be be used in Windows function calls.

    :param file python_file:
        The Python file object to convert to a Windows handle.

    :raises ValueError:
        Raised if ``python_file`` is a valid file object
        but is not open.

    :return:
        Returns a Windows handle object which is pointing at
        the provided ``python_file`` object.
    """
    _, library = Library.load()
    input_check("python_file", python_file, Enums.PYFILE)

    # WARNING:
    #   Be aware that passing in an invalid file descriptor
    #   number can crash Python.
    return library.handle_from_fd(python_file.fileno())


def CreatePipe(nSize=0, lpPipeAttributes=None):
    """
    Creates an anonymous pipe and returns the read and write handles.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/aa365152
        https://msdn.microsoft.com/en-us/library/aa379560

    >>> from pywincffi.core.ffi import Library
    >>> ffi, library = Library.load()
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
    """
    input_check("nSize", nSize, integer_types)
    input_check("lpPipeAttributes", lpPipeAttributes, (NoneType, dict))
    ffi, library = Library.load()

    hReadPipe = ffi.new("PHANDLE")
    hWritePipe = ffi.new("PHANDLE")

    if lpPipeAttributes is None:
        lpPipeAttributes = ffi.NULL

    code = library.CreatePipe(hReadPipe, hWritePipe, lpPipeAttributes, nSize)
    error_check("CreatePipe", code=code, expected=Enums.NON_ZERO)

    return hReadPipe[0], hWritePipe[0]


def SetNamedPipeHandleState(
        hNamedPipe,
        lpMode=None, lpMaxCollectionCount=None, lpCollectDataTimeout=None):
    """
    Sets the read and blocking mode of the specified ``hNamedPipe``.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/aa365787

    :param handle hNamedPipe:
        A handle to the named pipe instance.

    :keyword int lpMode:
        The new pipe mode which is a combination of read mode:

            * ``PIPE_READMODE_BYTE``
            * ``PIPE_READMODE_MESSAGE``

        And a wait-mode flag:

            * ``PIPE_WAIT``
            * ``PIPE_NOWAIT``

    :keyword int lpMaxCollectionCount:
        The maximum number of bytes collected.

    :keyword int lpCollectDataTimeout:
        The maximum time, in milliseconds, that can pass before a
        remote named pipe transfers information
    """
    input_check("hNamedPipe", hNamedPipe, Enums.HANDLE)
    ffi, library = Library.load()

    if lpMode is None:
        lpMode = ffi.NULL
    else:
        input_check("lpMode", lpMode, integer_types)
        lpMode = ffi.new("LPDWORD", lpMode)

    if lpMaxCollectionCount is None:
        lpMaxCollectionCount = ffi.NULL
    else:
        input_check(
            "lpMaxCollectionCount", lpMaxCollectionCount, integer_types)
        lpMaxCollectionCount = ffi.new("LPDWORD", lpMaxCollectionCount)

    if lpCollectDataTimeout is None:
        lpCollectDataTimeout = ffi.NULL
    else:
        input_check(
            "lpCollectDataTimeout", lpCollectDataTimeout, integer_types)
        lpCollectDataTimeout = ffi.new("LPDWORD", lpCollectDataTimeout)

    code = library.SetNamedPipeHandleState(
        hNamedPipe,
        lpMode,
        lpMaxCollectionCount,
        lpCollectDataTimeout
    )
    error_check("SetNamedPipeHandleState", code=code, expected=Enums.NON_ZERO)


def PeekNamedPipe(hNamedPipe, nBufferSize):
    """
    Copies data from a pipe into a buffer without removing it
    from the pipe.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/aa365779

    :param handle hNamedPipe:
        The handele to the pipe object we want to peek into.

    :param int nBufferSize:
        The number of bytes to 'peek' into the pipe.

    :rtype: :class:`PeekNamedPipeResult`
    :return:
        Returns an instance of :class:`PeekNamedPipeResult` which
        contains the buffer read, number of bytes read and the result.
    """
    input_check("hNamedPipe", hNamedPipe, Enums.HANDLE)
    input_check("nBufferSize", nBufferSize, integer_types)
    ffi, library = Library.load()

    # Outputs
    lpBuffer = ffi.new("LPVOID[%d]" % nBufferSize)
    lpBytesRead = ffi.new("LPDWORD")
    lpTotalBytesAvail = ffi.new("LPDWORD")
    lpBytesLeftThisMessage = ffi.new("LPDWORD")

    code = library.PeekNamedPipe(
        hNamedPipe,
        lpBuffer,
        nBufferSize,
        lpBytesRead,
        lpTotalBytesAvail,
        lpBytesLeftThisMessage
    )
    error_check("PeekNamedPipe", code=code, expected=Enums.NON_ZERO)

    return PeekNamedPipeResult(
        lpBuffer=lpBuffer,
        lpBytesRead=lpBytesRead[0],
        lpTotalBytesAvail=lpTotalBytesAvail[0],
        lpBytesLeftThisMessage=lpBytesLeftThisMessage[0]
    )


def WriteFile(hFile, lpBuffer, lpOverlapped=None):
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

    :type lpOverlapped: None or OVERLAPPED
    :param lpOverlapped:
        None or a pointer to a ``OVERLAPPED`` structure.  See Microsoft's
        documentation for intended usage and below for an example of this
        struct.

        >>> from pywincffi.core.ffi import Library
        >>> ffi, library = Library.load()
        >>> hFile = None # normally, this would be a handle
        >>> lpOverlapped = ffi.new(
        ...     "OVERLAPPED[1]", [{
        ...         "hEvent": hFile
        ...     }]
        ... )
        >>> bytes_written = WriteFile(
        ...     hFile, "Hello world", lpOverlapped=lpOverlapped)

    :returns:
        Returns the number of bytes written
    """
    ffi, library = Library.load()

    if lpOverlapped is None:
        lpOverlapped = ffi.NULL

    input_check("hFile", hFile, Enums.HANDLE)
    input_check("lpBuffer", lpBuffer, Enums.UTF8)
    input_check("lpOverlapped", lpOverlapped, Enums.OVERLAPPED)

    # Prepare string and outputs
    nNumberOfBytesToWrite = len(lpBuffer)
    lpBuffer = ffi.new("wchar_t[%d]" % nNumberOfBytesToWrite, lpBuffer)
    bytes_written = ffi.new("LPDWORD")

    code = library.WriteFile(
        hFile, lpBuffer, ffi.sizeof(lpBuffer), bytes_written, lpOverlapped)
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
    :param lpOverlapped:
        None or a pointer to a ``OVERLAPPED`` structure.  See Microsoft's
        documentation for intended usage and below for an example of this
        struct.

        >>> from pywincffi.core.ffi import Library
        >>> ffi, library = Library.load()
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
    ffi, library = Library.load()

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


def CloseHandle(hObject):
    """
    Closes an open object handle.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms724211

    :param handle hObject:
        The handle object to close.
    """
    input_check("hObject", hObject, Enums.HANDLE)
    _, library = Library.load()

    code = library.CloseHandle(hObject)
    error_check("CloseHandle", code=code, expected=Enums.NON_ZERO)


def GetStdHandle(nStdHandle):
    """
    Retrieves a handle to the specified standard
    device (standard input, standard output, or standard error).

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms683231

    :param int nStdHandle:
        The standard device to retrieve

    :rtype: handle
    :return:
        Returns a handle to the standard device retrieved.
    """
    _, library = Library.load()
    input_check("nStdHandle", nStdHandle,
                allowed_values=(library.STD_INPUT_HANDLE,
                                library.STD_OUTPUT_HANDLE,
                                library.STD_ERROR_HANDLE))

    handle = library.GetStdHandle(nStdHandle)

    if handle == library.INVALID_HANDLE_VALUE:  # pragma: no cover
        raise WindowsAPIError(
            "GetStdHandle", "Invalid Handle", library.INVALID_HANDLE_VALUE,
            "not %s" % library.INVALID_HANDLE_VALUE)

    return handle
