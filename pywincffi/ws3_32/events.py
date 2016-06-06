"""
Events
------

A module containing Windows functions for working with events.
"""

from six import integer_types

from pywincffi.core import dist
from pywincffi.core.checks import Enums, input_check, error_check
from pywincffi.exceptions import WindowsAPIError


def WSAEventSelect(sock, hEventObject, lNetworkEvents):
    """
    Specifies an event object to be associated with the specified set of
    FD_XXX network events.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms741576

    :param int sock:
        A descriptor identify the socket.

    :param handle hEventObject:
        A handle which identifies the event object to be associated
        with the network events.

    :param int lNetworkEvents:
        A bitmask which specifies the combination of ``FD_XXX`` network
        events which the application has interest in.
    """
    input_check("sock", sock, integer_types)
    input_check("hEventObject", hEventObject, Enums.HANDLE)
    input_check("lNetworkEvents", lNetworkEvents, integer_types)

    ffi, library = dist.load()

    # TODO: `sock` needs conversion
    code = library.WSAEventSelect(
        sock,
        ffi.cast("WSAEVENT", hEventObject),
        ffi.cast("long", lNetworkEvents)
    )

    if code == library.SOCKET_ERROR:
        errno = WSAGetLastError()
        raise WindowsAPIError(
            "WSAEventSelect", "Socket error %d" % errno, errno)

    error_check("WSAEventSelect", code, expected=0)


def WSAGetLastError():
    """
    Returns the last error status for a windows socket operation.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms741580
    """
    _, library = dist.load()
    return library.WSAGetLastError()
