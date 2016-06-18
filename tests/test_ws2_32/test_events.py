from pywincffi.dev.testutil import TestCase
from pywincffi.ws2_32 import WSAGetLastError


class TestWSAGetLastError(TestCase):
    """
    Tests for ``pywincffi.ws2_32.events.WSAGetLastError``
    """
    def test_get_last_error(self):
        self._ws2_32.WSASetLastError(4242)
        self.assertEqual(WSAGetLastError(), 4242)
