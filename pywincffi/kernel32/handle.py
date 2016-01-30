"""
Handles
-------

A module containing general functions for working with handle
objects.
"""

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
            "not %s" % INVALID_HANDLE_VALUE)

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
