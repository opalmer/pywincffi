"""
Overlapped
----------

A module containing Windows functions for working with OVERLAPPED objects.
"""

from pywincffi.core import dist
from pywincffi.core.checks import NON_ZERO, input_check, error_check
from pywincffi.exceptions import WindowsAPIError
from pywincffi.wintypes import HANDLE, OVERLAPPED, wintype_to_cdata


def GetOverlappedResult(hFile, lpOverlapped, bWait):
    """
    Retrieves the results of an overlapped operation on the specified file,
    named pipe, or communications device. To specify a timeout interval or
    wait on an alertable thread, use GetOverlappedResultEx.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms683209

    :param pywincffi.wintypes.HANDLE hFile:
        A handle to the file, named pipe, or communications device.
        This is the same handle that was specified when the overlapped
        operation was started by a call to the ReadFile, WriteFile,
        ConnectNamedPipe, TransactNamedPipe, DeviceIoControl, or WaitCommEvent
        function.

    :param pywincffi.wintypes.OVERLAPPED lpOverlapped:
        The an OVERLAPPED object that was specified when the overlapped
        operation was started

    :param bool bWait:
        If this parameter is TRUE, and the Internal member of the lpOverlapped
        structure is STATUS_PENDING, the function does not return until the
        operation has been completed. If this parameter is FALSE and the
        operation is still pending, the function returns FALSE and the
        GetLastError function returns ERROR_IO_INCOMPLETE

    :returns:
        The number of bytes that were actually transferred by a read or write
        operation. For a TransactNamedPipe operation, this is the number of
        bytes that were read from the pipe. For a DeviceIoControl operation,
        this is the number of bytes of output data returned by the device
        driver. For a ConnectNamedPipe or WaitCommEvent operation, this value
        is undefined.
    """
    input_check("hFile", hFile, HANDLE)
    input_check("lpOverlapped", lpOverlapped, OVERLAPPED)
    input_check("bWait", bWait, allowed_values=(True, False))

    ffi, library = dist.load()

    lpNumberOfBytesTransferred = ffi.new("DWORD[1]")

    result = library.GetOverlappedResult(
        wintype_to_cdata(hFile),
        wintype_to_cdata(lpOverlapped),
        lpNumberOfBytesTransferred,
        ffi.cast("BOOL", bWait),
    )

    try:
        error_check("GetOverlappedResult", result, NON_ZERO)
    except WindowsAPIError as error:
        if error.errno != library.ERROR_ALREADY_EXISTS:
            raise

    return int(lpNumberOfBytesTransferred[0])
