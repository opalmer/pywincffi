import socket

from pywincffi.core import dist
from pywincffi.dev.testutil import TestCase, mock_library
from pywincffi.exceptions import WindowsAPIError
from pywincffi.kernel32 import CloseHandle
from pywincffi.wintypes import LPWSANETWORKEVENTS, socket_from_object
from pywincffi.ws2_32 import (
    WSAGetLastError, WSACreateEvent, WSAEventSelect, WSAEnumNetworkEvents)


class EventsCase(TestCase):
    """
    Has some common methods used by tests in this module
    """
    def tearDown(self):
        super(EventsCase, self).tearDown()
        self.assertEqual(WSAGetLastError(), 0)

    def create_wsaevent(self):
        event = WSACreateEvent()
        self.addCleanup(CloseHandle, event)
        return event

    def create_socket_pair(self):
        """
        Creates a local socket listening on a random port.
        """
        # Establish the server's socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addCleanup(server.close)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addCleanup(client.close)
        return server, client


class TestWSAGetLastError(TestCase):
    """
    Tests for ``pywincffi.ws2_32.events.WSAGetLastError``
    """
    def test_get_last_error(self):
        self.addCleanup(self.WSASetLastError, 0)
        self.WSASetLastError(4242)
        self.assertEqual(WSAGetLastError(), 4242)


class TestWSACreateEvent(TestCase):
    """
    Tests for ``pywincffi.ws2_32.events.WSACreateEvent``
    """
    def test_invalid_event(self):
        with mock_library(wsa_invalid_event=lambda _: True):
            with self.assertRaises(WindowsAPIError):
                WSACreateEvent()


class TestWSAEventSelect(EventsCase):
    """
    Tests for ``pywincffi.ws2_32.events.WSAEventSelect``
    """
    def test_basic_call(self):
        # Establish a simple socket server and client
        _, library = dist.load()
        sock, _, = self.create_socket_pair()

        # Setup the event
        event = self.create_wsaevent()
        WSAEventSelect(
            socket_from_object(sock),
            event,
            library.FD_WRITE | library.FD_ACCEPT | library.FD_CONNECT
        )

    def test_socket_error(self):
        def wrapped(*_):
            _, library = dist.load()
            return library.SOCKET_ERROR

        with mock_library(WSAEventSelect=wrapped):
            # Establish a simple socket server and client
            _, library = dist.load()
            sock, _ = self.create_socket_pair()

            # Setup the event
            event = self.create_wsaevent()

            with self.assertRaises(WindowsAPIError):
                WSAEventSelect(
                    socket_from_object(sock),
                    event,
                    library.FD_WRITE | library.FD_ACCEPT | library.FD_CONNECT
                )


class TestWSAEnumNetworkEvents(EventsCase):
    """
    Tests for ``pywincffi.ws2_32.events.WSAEnumNetworkEvents``
    """
    def test_basic_call(self):
        _, library = dist.load()
        sock, _ = self.create_socket_pair()
        events = WSAEnumNetworkEvents(socket_from_object(sock))
        self.assertIsInstance(events, LPWSANETWORKEVENTS)
        self.assertEqual(events.iErrorCode, tuple([0] * library.FD_MAX_EVENTS))

    def test_triggers_accept_event(self):
        _, library = dist.load()
        sock_server, sock_client = self.create_socket_pair()
        sock_server_wintype = socket_from_object(sock_server)

        # Listen on one socket and then connect with another.  This should
        # cause an FD_ACCEPT network event to occur.
        sock_server.bind(("127.0.0.1", 0))
        sock_server.listen(0)
        _, port = sock_server.getsockname()
        sock_client.connect(("127.0.0.1", port))

        event = self.create_wsaevent()
        WSAEventSelect(sock_server_wintype, event, library.FD_ACCEPT)
        events = WSAEnumNetworkEvents(sock_server_wintype)
        self.assertEqual(events.lNetworkEvents, library.FD_ACCEPT)

    def test_triggers_write_event(self):
        _, library = dist.load()
        sock_server, sock_client = self.create_socket_pair()
        sock_client_wintype = socket_from_object(sock_client)

        # Listen on one socket and then connect with another.  This should
        # cause an FD_ACCEPT network event to occur.
        sock_server.bind(("127.0.0.1", 0))
        sock_server.listen(0)
        _, port = sock_server.getsockname()
        sock_client.connect(("127.0.0.1", port))
        sock_client.send(b"Hello world")

        event = self.create_wsaevent()
        WSAEventSelect(sock_client_wintype, event, library.FD_WRITE)
        events = WSAEnumNetworkEvents(sock_client_wintype)
        self.assertEqual(events.lNetworkEvents, library.FD_WRITE)
