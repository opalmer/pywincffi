"""
Handles
-------

A module containing general functions for working with handle
objects.
"""

from six import integer_types

from pywincffi.core import dist
from pywincffi.core.checks import Enums, input_check, error_check
from pywincffi.exceptions import WindowsAPIError


INVALID_HANDLE_VALUE = -1


def handle_from_file(python_file):
    """
    Given a standard Python file object produce a Windows
    handle object that be be used in Windows function calls.

    :param file python_file:
        The Python file object to convert to a Windows handle.

    :return:
        Returns a Windows handle object which is pointing at
        the provided ``python_file`` object.
    """
    _, library = dist.load()
    input_check("python_file", python_file, Enums.PYFILE)

    # WARNING:
    #   Be aware that passing in an invalid file descriptor
    #   number can crash Python.  The input_check function
    #   above should handle this for us by checking to
    #   ensure the file descriptor is valid first.
    return library.handle_from_fd(python_file.fileno())


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
    _, library = dist.load()
    input_check("nStdHandle", nStdHandle,
                allowed_values=(library.STD_INPUT_HANDLE,
                                library.STD_OUTPUT_HANDLE,
                                library.STD_ERROR_HANDLE))

    handle = library.GetStdHandle(nStdHandle)

    if handle == INVALID_HANDLE_VALUE:  # pragma: no cover
        raise WindowsAPIError(
            "GetStdHandle", "Invalid Handle", INVALID_HANDLE_VALUE,
            expected_return_code="not %r" % INVALID_HANDLE_VALUE)

    return handle


def CloseHandle(hObject):
    """
    Closes an open object handle.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms724211

    :param handle hObject:
        The handle object to close.
    """
    input_check("hObject", hObject, Enums.HANDLE)
    _, library = dist.load()

    code = library.CloseHandle(hObject)
    error_check("CloseHandle", code=code, expected=Enums.NON_ZERO)


def WaitForSingleObject(hHandle, dwMilliseconds):
    """
    Waits for the specified object to be in a signaled state
    or for ``dwMiliseconds`` to elapse.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms687032

    :param handle hHandle:
        The handle to wait on.

    :param int dwMilliseconds:
        The time-out interval.
    """
    input_check("hHandle", hHandle, Enums.HANDLE)
    input_check("dwMilliseconds", dwMilliseconds, integer_types)

    ffi, library = dist.load()
    result = library.WaitForSingleObject(
        hHandle, ffi.cast("DWORD", dwMilliseconds)
    )

    if result == library.WAIT_FAILED:
        raise WindowsAPIError(
            "WaitForSingleObject", "Wait Failed", ffi.getwinerror()[-1],
            return_code=result, expected_return_code="not %s" % result)

    error_check("WaitForSingleObject")

    return result


def GetHandleInformation(hObject):
    """
    Returns properties of an object handle.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms724329

    :param handle hObject:
        A handle to an object whose information is to be retrieved.

    :rtype: int
    :return:
        Returns the set of bit flags that specify properties of ``hObject``.
    """
    input_check("hObject", hObject, Enums.HANDLE)
    ffi, library = dist.load()

    lpdwFlags = ffi.new("LPDWORD")
    code = library.GetHandleInformation(hObject, lpdwFlags)
    error_check("GetHandleInformation", code=code, expected=Enums.NON_ZERO)

    return lpdwFlags[0]


def SetHandleInformation(hObject, dwMask, dwFlags):
    """
    Sets properties of an object handle.

    .. seealso::

        https://msdn.microsoft.com/en-us/ms724935

    :param handle hObject:
        A handle to an object whose information is to be set.

    :param int dwMask:
        A mask that specifies the bit flags to be changed.

    :param int dwFlags:
        Set of bit flags that specifies properties of ``hObject``.
    """
    input_check("hObject", hObject, Enums.HANDLE)
    input_check("dwMask", dwMask, integer_types)
    input_check("dwFlags", dwFlags, integer_types)
    ffi, library = dist.load()

    code = library.SetHandleInformation(
        hObject,
        ffi.cast("DWORD", dwMask),
        ffi.cast("DWORD", dwFlags)
    )
    error_check("SetHandleInformation", code=code, expected=Enums.NON_ZERO)
