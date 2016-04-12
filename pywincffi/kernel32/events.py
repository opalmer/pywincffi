"""
Events
------

A module containing Windows functions for working with events.
"""

from six import string_types

from pywincffi.core import dist
from pywincffi.core.checks import Enums, input_check, error_check
from pywincffi.exceptions import WindowsAPIError
from pywincffi.util import string_to_cdata


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

    :keyword struct lpEventAttributes:
        A pointer to a ``SECURITY_ATTRIBUTES`` structure.  If not provided
        then by default the handle cannot be inherited by a subprocess.

    :keyword str lpName:
        The optional case-sensitive name of the event.  If not provided then
        the event will be created without an explicit name.

    :returns:
        Returns a handle to the event.  If an event by the given name already
        exists then it will be returned instead of creating a new event.
    """
    input_check("bManualReset", bManualReset, bool)
    input_check("bInitialState", bInitialState, bool)

    ffi, library = dist.load()

    if lpName is None:
        lpName = ffi.NULL
    else:
        input_check("lpName", lpName, string_types)
        lpName = string_to_cdata(lpName)

    if lpEventAttributes is None:
        lpEventAttributes = ffi.NULL
    else:
        input_check(
            "lpEventAttributes", lpEventAttributes,
            allowed_types=Enums.SECURITY_ATTRIBUTES)

    handle = library.CreateEvent(
        lpEventAttributes,
        ffi.cast("BOOL", bManualReset),
        ffi.cast("BOOL", bInitialState),
        lpName
    )

    try:
        error_check("CreateEvent")
    except WindowsAPIError as error:
        if error.errno != library.ERROR_ALREADY_EXISTS:
            raise

    return handle
