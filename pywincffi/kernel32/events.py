"""
Events
------

A module containing Windows functions for working with events.
"""

from six import integer_types, text_type

from pywincffi.core import dist
from pywincffi.core.checks import Enums, input_check, error_check, NoneType
from pywincffi.exceptions import WindowsAPIError
from pywincffi.wintypes import HANDLE, SECURITY_ATTRIBUTES, wintype_to_cdata


def CreateEvent(
        bManualReset, bInitialState, lpEventAttributes=None, lpName=None):
    """
    Creates or opens an named or unnamed event object.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms682396

    :param bool bManualReset:
        If True then this function will create a manual reset
        event which must be manually reset with :func:`ResetEvent`.  Refer
        to the msdn documentation for full information.

    :param bool bInitialState:
        If True the initial state will be 'signaled'.

    :keyword :class:`pywincffi.wintypes.SECURITY_ATTRIBUTES` lpEventAttributes:
        If not provided then, by default, the handle cannot be inherited
        by a subprocess.

    :keyword str lpName:
        Type is ``unicode`` on Python 2, ``str`` on Python 3.
        The optional case-sensitive name of the event.  If not provided then
        the event will be created without an explicit name.

    :returns:
        Returns a :class:`pywincffi.wintypes.HANDLE` to the event. If an event
        by the given name already exists then it will be returned instead of
        creating a new event.
    """
    input_check("bManualReset", bManualReset, bool)
    input_check("bInitialState", bInitialState, bool)

    ffi, library = dist.load()

    if lpName is None:
        lpName = ffi.NULL
    else:
        input_check("lpName", lpName, text_type)

    input_check(
        "lpEventAttributes", lpEventAttributes,
        allowed_types=(SECURITY_ATTRIBUTES, NoneType)
    )

    handle = library.CreateEvent(
        wintype_to_cdata(lpEventAttributes),
        ffi.cast("BOOL", bManualReset),
        ffi.cast("BOOL", bInitialState),
        lpName
    )

    try:
        error_check("CreateEvent")
    except WindowsAPIError as error:
        if error.errno != library.ERROR_ALREADY_EXISTS:
            raise

    return HANDLE(handle)


def OpenEvent(dwDesiredAccess, bInheritHandle, lpName):
    """
    Opens an existing named event.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms684305

    :param int dwDesiredAccess:
        The access desired for the event object.

    :param bool bInheritHandle:
    :param str lpName:
        Type is ``unicode`` on Python 2, ``str`` on Python 3.

    :return:
        Returns a :class:`pywincffi.wintypes.HANDLE` to the event.
    """
    input_check("dwDesiredAccess", dwDesiredAccess, integer_types)
    input_check("bInheritHandle", bInheritHandle, bool)
    input_check("lpName", lpName, text_type)

    ffi, library = dist.load()

    handle = library.OpenEvent(
        ffi.cast("DWORD", dwDesiredAccess),
        ffi.cast("BOOL", bInheritHandle),
        lpName
    )
    error_check("OpenEvent")
    return HANDLE(handle)


def ResetEvent(hEvent):
    """
    Sets the specified event object to the nonsignaled state.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms684305

    :param pywincffi.wintypes.HANDLE hEvent:
        A handle to the event object to be reset. The handle must
        have the ``EVENT_MODIFY_STATE`` access right.
    """
    input_check("hEvent", hEvent, HANDLE)

    _, library = dist.load()
    code = library.ResetEvent(wintype_to_cdata(hEvent))
    error_check("ResetEvent", code=code, expected=Enums.NON_ZERO)
