"""
Errors
------

A module containing functions for dealing with API errors.
"""

from six import integer_types

from pywincffi.core import dist
from pywincffi.core.checks import input_check


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
