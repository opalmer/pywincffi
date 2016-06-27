from pywincffi.core import dist
from pywincffi.dev.testutil import TestCase
from pywincffi.wintypes import HANDLE


class TestHANDLE(TestCase):
    """
    Tests for :class:`pywincffi.wintypes.HANDLE`
    """
    def test_instantiate(self):
        h = HANDLE()
        self.assertIsInstance(h, HANDLE)

    def test_compare_equal_highlevel(self):
        h1 = HANDLE()
        h2 = HANDLE()
        self.assertIsNot(h1, h2)
        self.assertEqual(h1, h2)

    def _handle_from_int(self, int_data):
        ffi, _ = dist.load()
        cdata = ffi.new("HANDLE[1]")
        cdata[0] = ffi.cast("HANDLE", int_data)
        return HANDLE(cdata[0])

    def test_compare_equal_lowlevel(self):
        h1 = self._handle_from_int(42)
        h2 = self._handle_from_int(42)
        self.assertIsNot(h1, h2)
        self.assertEqual(h1, h2)

    def test_compare_different_lowlevel(self):
        h1 = self._handle_from_int(42)
        h2 = self._handle_from_int(43)
        self.assertIsNot(h1, h2)
        self.assertNotEqual(h1, h2)

    def test_compare_wrong_type(self):
        h = HANDLE()
        with self.assertRaises(TypeError):
            if h == 0:
                pass
