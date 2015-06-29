import os
import tempfile
from textwrap import dedent

from cffi import FFI

from pywincffi import core
from pywincffi.testutil import TestCase


class TestFFI(TestCase):
    """
    Tests the ``pywinffi.core.library.ffi`` global.
    """
    def test_unicode(self):
        self.assertTrue(core.ffi._windows_unicode)

    def test_instance(self):
        self.assertIsInstance(core.ffi, FFI)


class TestBind(TestCase):
    def test_bind(self):
        print(core)
        print(dir(core))
        ffi = FFI()
        ffi.set_unicode(True)

        fd, path = tempfile.mkstemp()
        self.addCleanup(self.remove, path)

        with os.fdopen(fd, "wb") as temp_stream:
            data = dedent("""
            #define PROCESS_QUERY_INFORMATION 0x0400
            """)
            temp_stream.write(data.encode())

        kernel32 = core.bind("kernel32", path, ffi_=ffi)
        self.assertEqual(kernel32.PROCESS_QUERY_INFORMATION, 0x0400)
