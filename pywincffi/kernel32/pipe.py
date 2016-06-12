"""
Pipe
----

A module for working with pipe objects in Windows.
"""

from collections import namedtuple

from six import integer_types

from pywincffi.core import dist
from pywincffi.core.checks import Enums, input_check, error_check, NoneType
from pywincffi.wintypes import SECURITY_ATTRIBUTES, HANDLE, wintype_to_cdata

PeekNamedPipeResult = namedtuple(
    "PeekNamedPipeResult",
    ("lpBuffer", "lpBytesRead", "lpTotalBytesAvail",
     "lpBytesLeftThisMessage")
)


def CreatePipe(nSize=0, lpPipeAttributes=None):
    """
    Creates an anonymous pipe and returns the read and write handles.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/aa365152
        https://msdn.microsoft.com/en-us/library/aa379560

    >>> from pywincffi.core import dist
    >>> from pywincffi.kernel32 import CreatePipe
    >>> from pywincffi.wintypes import SECURITY_ATTRIBUTES
    >>> lpPipeAttributes = SECURITY_ATTRIBUTES()
    >>> lpPipeAttributes.bInheritHandle = True
    >>> reader, writer = CreatePipe(lpPipeAttributes=lpPipeAttributes)

    :keyword int nSize:
        The size of the buffer in bytes.  Passing in 0, which is the default
        will cause the system to use the default buffer size.

    :keyword pywincffi.wintypes.SECURITY_ATTRIBUTES lpPipeAttributes:
        The security attributes to apply to the handle. By default
        ``NULL`` will be passed in, meaning the handle we create
        cannot be inherited.  For more detailed information see the links
        below.

    :return:
        Returns a tuple of :class:`pywincffi.wintype.HANDLE` containing the
        reader and writer ends of the pipe that was created.  The user of this
        function is responsible for calling CloseHandle at some point.
    """
    input_check("nSize", nSize, integer_types)
    input_check(
        "lpPipeAttributes", lpPipeAttributes,
        allowed_types=(NoneType, SECURITY_ATTRIBUTES)
    )
    lpPipeAttributes = wintype_to_cdata(lpPipeAttributes)

    ffi, library = dist.load()

    hReadPipe = ffi.new("PHANDLE")
    hWritePipe = ffi.new("PHANDLE")

    code = library.CreatePipe(hReadPipe, hWritePipe, lpPipeAttributes, nSize)
    error_check("CreatePipe", code=code, expected=Enums.NON_ZERO)

    return HANDLE(hReadPipe[0]), HANDLE(hWritePipe[0])


def SetNamedPipeHandleState(
        hNamedPipe,
        lpMode=None, lpMaxCollectionCount=None, lpCollectDataTimeout=None):
    """
    Sets the read and blocking mode of the specified ``hNamedPipe``.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/aa365787

    :param pywincffi.wintypes.HANDLE hNamedPipe:
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
    input_check("hNamedPipe", hNamedPipe, HANDLE)
    ffi, library = dist.load()

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
        wintype_to_cdata(hNamedPipe),
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

    :param pywincffi.wintypes.HANDLE hNamedPipe:
        The handele to the pipe object we want to peek into.

    :param int nBufferSize:
        The number of bytes to 'peek' into the pipe.

    :rtype: PeekNamedPipeResult
    :return:
        Returns an instance of :class:`PeekNamedPipeResult` which
        contains the buffer read, number of bytes read and the result.
    """
    input_check("hNamedPipe", hNamedPipe, HANDLE)
    input_check("nBufferSize", nBufferSize, integer_types)
    ffi, library = dist.load()

    # Outputs
    lpBuffer = ffi.new("LPVOID[%d]" % nBufferSize)
    lpBytesRead = ffi.new("LPDWORD")
    lpTotalBytesAvail = ffi.new("LPDWORD")
    lpBytesLeftThisMessage = ffi.new("LPDWORD")

    code = library.PeekNamedPipe(
        wintype_to_cdata(hNamedPipe),
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
