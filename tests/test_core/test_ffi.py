from textwrap import dedent
from os.path import dirname, join

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

from cffi import FFI
from six.moves import builtins

import pywincffi
from pywincffi.core.ffi import Library, new_ffi, ffi
from pywincffi.core.testutil import TestCase
from pywincffi.exceptions import HeaderNotFoundError


class TestFFI(TestCase):
    """
    Tests the ``pywinffi.core.ffi.ffi`` global.
    """
    def test_unicode(self):
        self.assertTrue(ffi._windows_unicode)

    def test_instance(self):
        self.assertIsInstance(ffi, FFI)


class TestLibraryLoadHeader(TestCase):
    """
    Tests for ``pywincffi.core.ffi.Library._load_header``
    """
    def test_loads_header_from_correct_path(self):
        path = join(dirname(pywincffi.__file__), "headers", "kernel32.h")
        with open(path, "rb") as stream:
            header = stream.read().decode()

        self.assertEqual(Library._load_header("kernel32.h"), header)

    def test_returns_none_when_header_not_found(self):
        self.assertIsNone(Library._load_header("foobar"))

    def test_raises_non_not_found_errors(self):
        def side_effect(*args, **kwargs):
            raise OSError(42, "fail")

        with patch.object(builtins, "open", side_effect=side_effect):
            with self.assertRaises(OSError) as raised_error:
                Library._load_header("kernel32")
        self.assertEqual(raised_error.exception.errno, 42)


class TestLibraryLoad(TestCase):
    """
    Tests for ``pywincffi.core.ffi.Library.load``
    """
    def setUp(self):
        self._cache = Library.CACHE.copy()
        Library.CACHE.clear()

    def tearDown(self):
        Library.CACHE.clear()
        Library.CACHE.update(self._cache)

    def test_returns_cached(self):
        ffi_instance = new_ffi()
        Library.CACHE[ffi_instance] = {"foo_library1": True}
        self.assertIs(
            Library.load("foo_library1", ffi_instance=ffi_instance),
            True
        )

    def test_returns_cached_default_ffi_instance(self):
        Library.CACHE[ffi] = {"foo_library2": False}
        self.assertIs(Library.load("foo_library2"), False)

    def test_header_not_found(self):
        with patch.object(Library, "_load_header", return_value=None):
            with self.assertRaises(HeaderNotFoundError):
                Library.load("kernel32")

    def test_loads_library(self):
        fake_header = dedent("""
        #define HELLO_WORLD 42
        """)
        with patch.object(Library, "_load_header", return_value=fake_header):
            library = Library.load("kernel32")

        self.assertEqual(library.HELLO_WORLD, 42)

    def test_caches_library(self):
        fake_header = dedent("""
        #define HELLO_WORLD 42
        """)
        self.assertNotIn(ffi, Library.CACHE)
        with patch.object(Library, "_load_header", return_value=fake_header):
            library1 = Library.load("kernel32")
            self.assertIn(ffi, Library.CACHE)
            library2 = Library.load("kernel32")

        self.assertIs(Library.CACHE[ffi]["kernel32"], library1)
        self.assertIs(Library.CACHE[ffi]["kernel32"], library2)
