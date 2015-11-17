from textwrap import dedent
from os.path import dirname, join

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

from cffi import FFI

from pywincffi.core.ffi import Library
from pywincffi.core.testutil import TestCase
from pywincffi.exceptions import ResourceNotFoundError


class TestFFI(TestCase):
    """
    Tests the ``pywinffi.core.ffi.ffi`` global.
    """
    def test_unicode(self):
        ffi, _ = Library.load()
        self.assertTrue(ffi._windows_unicode)

    def test_instance(self):
        ffi, _ = Library.load()
        self.assertIsInstance(ffi, FFI)


class TestSourcePaths(TestCase):
    """
    Tests for ``pywincffi.core.ffi.Library.[HEADERS|SOURCES]``
    """
    def test_sources_exist(self):
        for path in Library.SOURCES:
            try:
                with open(path, "r"):
                    pass
            except (OSError, IOError, WindowsError) as error:
                self.fail("Failed to load %s: %s" % (path, error))

    def test_headers_exist(self):
        for path in Library.HEADERS:
            try:
                with open(path, "r"):
                    pass
            except (OSError, IOError, WindowsError) as error:
                self.fail("Failed to load %s: %s" % (path, error))


class TestLibraryLoad(TestCase):
    """
    Tests for ``pywincffi.core.ffi.Library.load``
    """
    def setUp(self):
        self._cache = Library.CACHE
        Library.CACHE = (None, None)

    def tearDown(self):
        Library.CACHE = self._cache

    def test_header_not_found(self):
        with patch.object(Library, "HEADERS", ("foobar", )):
            with self.assertRaises(ResourceNotFoundError):
                Library.load()

    def test_loads_library(self):
        fake_header = dedent("""
        #define HELLO_WORLD 42
        """)
        with patch.object(Library, "_load_files", return_value=fake_header):
            ffi, library = Library.load()

        self.assertEqual(library.HELLO_WORLD, 42)

    def test_caches_library(self):
        fake_header = dedent("""
        #define HELLO_WORLD 42
        """)
        with patch.object(Library, "_load_files", return_value=fake_header):
            ffi1, lib1 = Library.load()
            ffi2, lib2 = Library.load()
        self.assertIs(ffi1, ffi2)
        self.assertIs(lib1, lib2)
