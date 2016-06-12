"""
Synchronization
---------------

This module contains general functions for synchronizing objects and
events.  The functions provided in this module are parts of the ``kernel32``
library.

.. seealso::

    :mod:`pywincffi.user32.synchronization`
"""

from six import integer_types

from pywincffi.core import dist
from pywincffi.core.checks import input_check, error_check
from pywincffi.exceptions import WindowsAPIError
from pywincffi.wintypes import HANDLE, wintype_to_cdata


def WaitForSingleObject(hHandle, dwMilliseconds):
    """
    Waits for the specified object to be in a signaled state
    or for ``dwMiliseconds`` to elapse.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms687032

    :param pywincffi.wintypes.HANDLE hHandle:
        The handle to wait on.

    :param int dwMilliseconds:
        The time-out interval.
    """
    input_check("hHandle", hHandle, HANDLE)
    input_check("dwMilliseconds", dwMilliseconds, integer_types)

    ffi, library = dist.load()
    result = library.WaitForSingleObject(
        wintype_to_cdata(hHandle), ffi.cast("DWORD", dwMilliseconds)
    )

    if result == library.WAIT_FAILED:
        raise WindowsAPIError(
            "WaitForSingleObject", "Wait Failed", ffi.getwinerror()[-1],
            return_code=result, expected_return_code="not %s" % result)

    error_check("WaitForSingleObject")

    return result
