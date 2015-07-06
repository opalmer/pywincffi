"""
Files
-----

A module containing common Windows file functions.
"""

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
