import socket

from pywincffi.core import dist
from pywincffi.dev.testutil import TestCase, mock_library
from pywincffi.exceptions import WindowsAPIError
from pywincffi.kernel32 import CloseHandle
from pywincffi.ws2_32 import WSAGetLastError, WSACreateEvent, WSAEventSelect
from pywincffi.wintypes import socket_from_object, wintype_to_cdata


class TestWSAGetLastError(TestCase):
    """
    Tests for ``pywincffi.ws2_32.events.WSAGetLastError``
    """
    def test_get_last_error(self):
        self._ws2_32.WSASetLastError(4242)
        self.assertEqual(WSAGetLastError(), 4242)


class TestWSACreateEvent(TestCase):
    """
    Tests for ``pywincffi.ws2_32.events.WSACreateEvent``
    """
    def test_create_event_call(self):
        event = WSACreateEvent()
        CloseHandle(event)

    def test_invalid_event(self):
        with mock_library(wsa_invalid_event=lambda _: True):
            with self.assertRaises(WindowsAPIError):
                WSACreateEvent()


class TestWSAEventSelect(TestCase):
    """
    Tests for ``pywincffi.ws2_32.events.WSAEventSelect``
    """
    def create_socket(self):
        _, library = dist.load()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addCleanup(sock.close)
        return socket_from_object(sock)

    def test_select_event_call(self):
        sock = self.create_socket()
        ffi, library = dist.load()
        event = WSACreateEvent()
        self.addCleanup(CloseHandle, event)
        WSAEventSelect(
            sock, event,
            library.FD_READ | library.FD_WRITE
        )
