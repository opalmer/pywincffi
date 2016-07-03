from pywincffi.core import dist
from pywincffi.dev.testutil import TestCase, mock_library
from pywincffi.exceptions import WindowsAPIError
from pywincffi.kernel32 import CloseHandle
from pywincffi.ws2_32 import WSAGetLastError, WSACreateEvent, WSAEventSelect
from pywincffi.wintypes import socket_from_object


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
    def test_event_select_basic_call(self):
        # Establish a simple socket server and client
        _, library = dist.load()
        server, client = self.create_socket()

        # Setup the event
        event = WSACreateEvent()
        self.addCleanup(CloseHandle, event)
        WSAEventSelect(
            socket_from_object(server),
            event,
            library.FD_WRITE | library.FD_ACCEPT | library.FD_CONNECT
        )
