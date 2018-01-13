"""
Errors
------

A module containing functions for dealing with API errors.
"""

from six import integer_types

from pywincffi.core import dist
from pywincffi.core.checks import NON_ZERO, input_check, error_check
from pywincffi.exceptions import WindowsAPIError


def GetLastError():
    """
    Returns the calling thread's last error code value.

    .. seealso::

         https://msdn.microsoft.com/en-us/library/ms679360

    :rtype: int
    """
    _, library = dist.load()
    return library.GetLastError()


def SetLastError(dwErrCode):
    """
    Sets the last error code for the calling thread.

    ... seealso::

        https://msdn.microsoft.com/en-us/ms680627

    :param int dwErrCode:
        The code to set.
    """
    _, library = dist.load()
    input_check("dwErrCode", dwErrCode, allowed_types=integer_types)
    library.SetLastError(dwErrCode)


def get_error_message(code=None):
    """
    This function will return the string representing a given error code.

    .. warning::

        This function makes no effort to validate if the current error code
        is indeed an error. As an example if the current error code is 0 then
        this function will return ``The operation completed successfully``
        which is not an error in most cases.

    :keyword int code:
        The optional error code to return a message for. If no
        code is provided :func:`GetLastError` will be called to
        get the current error code.

    :rtype: str
    """
    if code is None:
        code = GetLastError()

    ffi, _ = dist.load()
    return ffi.getwinerror(code)[-1]


def overlapped_error_check(function_name, code, lpOverlapped):
    """
    This function is a basic error checker for overlapped and non-overlapped
    cases. At the moment this is mainly intended for internal use and is used
    by function such as :func:`pywincffi.kernel32.file.ReadFile` and
    :func:`pywincffi.kernel32.file.WriteFile`.

    The implementation of this function is based on the following
    documentation by Microsoft:

      * https://support.microsoft.com/en-us/help/156932
      * https://msdn.microsoft.com/en-us/library/windows/desktop/ms686358
      * https://msdn.microsoft.com/en-us/library/windows/desktop/aa365683

    :param str function_name:
        The name of the function being checked.

    :param int code:
        The return code of the last function call.

    :param lpOverlapped:
        The overlapped structure being passed into the previously called
        function.
    """
    if lpOverlapped is None:
        error_check(function_name, code=code, expected=NON_ZERO)
        return

    # Overlapped IO case.
    _, library = dist.load()
    if GetLastError() == library.ERROR_IO_PENDING and code != 0:
        raise WindowsAPIError(
            function_name, get_error_message(code), code,
            return_code=code, expected_return_code=0)
