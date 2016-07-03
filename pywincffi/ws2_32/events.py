"""
Events
------

A module containing Windows functions for working with events.
"""

from six import integer_types

from pywincffi.core import dist
from pywincffi.core.checks import input_check, error_check
from pywincffi.exceptions import WindowsAPIError
from pywincffi.wintypes import (
    HANDLE, SOCKET, WSAEVENT, LPWSANETWORKEVENTS, wintype_to_cdata)


def WSAEventSelect(socket, hEventObject, lNetworkEvents):
    """
    Specifies an event object to be associated with the specified set of
    FD_XXX network events.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms741576

    :param pywincffi.wintypes.objects.SOCKET socket:
        The socket object to associate the selected network events with.

    :param pywincffi.wintypes.objects.WSAEVENT hEventObject:
        A handle which identifies the event object to be associated
        with the network events.

    :param int lNetworkEvents:
        A bitmask which specifies the combination of ``FD_XXX`` network
        events which the application has interest in.
    """
    input_check("socket", socket, allowed_types=(SOCKET, ))
    input_check("hEventObject", hEventObject, allowed_types=(HANDLE, ))
    input_check("lNetworkEvents", lNetworkEvents, integer_types)

    ffi, library = dist.load()

    code = library.WSAEventSelect(
        wintype_to_cdata(socket),
        wintype_to_cdata(hEventObject),
        ffi.cast("long", lNetworkEvents)
    )

    if code == library.SOCKET_ERROR:
        errno = WSAGetLastError()
        raise WindowsAPIError(
            "WSAEventSelect", "Socket error %d" % errno, errno)

    error_check("WSAEventSelect", code, expected=0)


def WSACreateEvent():
    """
    Creates a new event object.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms741561

    :returns:
        Returns a handle to a new event object.
    """
    _, library = dist.load()
    event = library.WSACreateEvent()

    if library.wsa_invalid_event(event):
        errno = WSAGetLastError()
        raise WindowsAPIError(
            "WSACreateEvent", "Socket error %d" % errno, errno)

    return HANDLE(event)


def WSAGetLastError():
    """
    Returns the last error status for a windows socket operation.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms741580
    """
    _, library = dist.load()
    return library.WSAGetLastError()


def WSAEnumNetworkEvents(socket, hEventObject=None):
    """
    Discovers occurrences of network events on the indicated ``socket``, clears
    internal events and optionally resets event objects.

    .. seealso::
        https://msdn.microsoft.com/en-us/ms741572

    :param pywincffi.wintypes.objects.SOCKET socket:
        The socket object to enumerate events for.

    :keyword pywincffi.wintypes.objects.WSAEVENT hEventObject:
        An optional handle identify an associated event object
        to be reset.

    :rtype: :class:`pywincffi.wintypes.structures.LPWSANETWORKEVENTS`
    :return:
    """
    input_check("socket", socket, allowed_types=(SOCKET, ))

    ffi, library = dist.load()
    if hEventObject is not None:
        input_check("hEventObject", hEventObject, allowed_types=(WSAEVENT, ))
        hEventObject = wintype_to_cdata(hEventObject)
    else:
        hEventObject = ffi.NULL

    lpNetworkEvents = LPWSANETWORKEVENTS()
    code = library.WSAEnumNetworkEvents(
        wintype_to_cdata(socket),
        hEventObject,
        wintype_to_cdata(lpNetworkEvents)
    )
    error_check("WSAEnumNetworkEvents", code=code, expected=0)

    return lpNetworkEvents
