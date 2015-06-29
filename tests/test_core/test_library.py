from cffi import FFI
from pywincffi.core import library
from pywincffi.testutil import TestCase


class TestFFI(TestCase):
    """
    Tests the ``pywinffi.core.library.ffi`` global.
    """
    def test_unicode(self):
        self.assertTrue(library.ffi._windows_unicode)

    def test_instance(self):
        self.assertIsInstance(library.ffi, FFI)
