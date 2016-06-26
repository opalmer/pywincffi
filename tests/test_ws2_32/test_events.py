from pywincffi.dev.testutil import TestCase
from pywincffi.exceptions import WindowsAPIError
from pywincffi.kernel32 import CloseHandle
from pywincffi.ws2_32 import WSAGetLastError, WSACreateEvent


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
        with self.mock_library(wsa_invalid_event=lambda _: True):
            with self.assertRaises(WindowsAPIError):
                WSACreateEvent()
