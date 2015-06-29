import os
import tempfile
from textwrap import dedent

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


class TestBind(TestCase):
    def test_bind(self):
        ffi = FFI()
        ffi.set_unicode(True)

        fd, path = tempfile.mkstemp()
        self.addCleanup(self.remove, path)

        with os.fdopen(fd, "wb") as temp_stream:
            data = dedent("""
            #define PROCESS_QUERY_INFORMATION 0x0400
            """)
            temp_stream.write(data.encode())

        kernel32 = library.bind("kernel32", path, ffi_=ffi)
        print(dir(kernel32))