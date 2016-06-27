"""
Functions
---------

This module provides various functions for converting and using Windows
types.
"""

from pywincffi.core import dist
from pywincffi.exceptions import InputError
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


def handle_from_file(file_):
    """
    Converts a standard Python file object into a :class:`HANDLE` object.

    .. warning::

        This function is mainly intended for internal use.  Passing in a file
        object with an invalid file descriptor may crash your interpreter.

    :param file file_:
        The Python file object to convert to a :class:`HANDLE` object.

    :raises InputError:
        Raised if ``file_`` does not appear to be a file object or is currently
        closed.

    :rtype: :class:`HANDLE`
    """
    try:
        fileno = file_.fileno()
    except AttributeError:
        raise InputError(
            "file_", file_, expected_types=None,
            message="Expected a file like object for `file_`")
    except ValueError:
        raise InputError(
            "file_", file_, expected_types=None,
            message="Expected an open file like object for `file_`")
    else:
        _, library = dist.load()
        return HANDLE(library.handle_from_fd(fileno))
