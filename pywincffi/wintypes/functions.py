"""
Functions
---------

This module provides various functions for converting and using Windows
types.
"""

from pywincffi.core import dist
from pywincffi.wintypes.objects import HANDLE


# pylint: disable=protected-access
def wintype_to_cdata(wintype):
    """
    Returns the underlying CFFI cdata object or ffi.NULL if wintype is None.
    Used internally in API wrappers to "convert" pywincffi's Python types to
    the required CFFI cdata objects when calling CFFI functions. Example:

    >>> from pywincffi.core import dist
    >>> from pywincffi.kernel32 import CreateEvent
    >>> from pywincffi.wintypes import wintype_to_cdata
    >>> ffi, lib = dist.load()
    >>> # Get an event HANDLE, using the wrapper: it's a Python HANDLE object.
    >>> hEvent = CreateEvent(False, False)
    >>> # Call ResetEvent directly without going through the wrapper:
    >>> hEvent_cdata = wintype_to_cdata(hEvent)
    >>> result = lib.ResetEvent(hEvent_cdata)

    :param wintype:
        A type derived from :class:`pywincffi.core.typesbase.CFFICDataWrapper`

    :return:
        The underlying CFFI <cdata> object, or ffi.NULL if wintype is None.
    """
    ffi, _ = dist.load()
    if wintype is None:
        return ffi.NULL
    elif isinstance(wintype, HANDLE):
        return wintype._cdata[0]
    else:
        return wintype._cdata
