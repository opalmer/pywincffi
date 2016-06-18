"""
Events
------

A module containing Windows functions for working with events.
"""

from six import integer_types

from pywincffi.core import dist
from pywincffi.core.checks import input_check, error_check
from pywincffi.exceptions import WindowsAPIError
from pywincffi.wintypes import HANDLE, SOCKET, wintype_to_cdata


def WSAEventSelect(socket, hEventObject, lNetworkEvents):
    """
    Specifies an event object to be associated with the specified set of
    FD_XXX network events.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms741576

    :param int socket:
        A descriptor identify the socket.

    :param :class:`pywincffi.wintypes.WSAEVENT` hEventObject:
        A handle which identifies the event object to be associated
        with the network events.

    :param int lNetworkEvents:
        A bitmask which specifies the combination of ``FD_XXX`` network
        events which the application has interest in.
    """
    input_check(
        "socket", socket, allowed_types=(SOCKET, ))
    input_check(
        "hEventObject", hEventObject,
        allowed_types=(HANDLE, )
    )
    input_check("lNetworkEvents", lNetworkEvents, integer_types)

    ffi, library = dist.load()

    # TODO: `socket` needs conversion
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
    result = library.WSACreateEvent()

    if result == library.WSA_INVALID_EVENT:
        errno = WSAGetLastError()
        raise WindowsAPIError(
            "WSACreateEvent", "Socket error %d" % errno, errno)

    return result


def WSAGetLastError():
    """
    Returns the last error status for a windows socket operation.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms741580
    """
    _, library = dist.load()
    return library.WSAGetLastError()
