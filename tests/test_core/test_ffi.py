import os
import tempfile
from textwrap import dedent
from os.path import dirname, join

from cffi import FFI
from mock import Mock, patch

from pywincffi.core import ffi
from pywincffi.core.ffi import new_ffi
from pywincffi.core.testutil import TestCase
from pywincffi.exceptions import WindowsAPIError, InputError


class TestFFI(TestCase):
    """
    Tests the ``pywinffi.core.ffi.ffi`` global.
    """
    def test_unicode(self):
        self.assertTrue(ffi.ffi._windows_unicode)

    def test_instance(self):
        self.assertIsInstance(ffi.ffi, FFI)


class TestBind(TestCase):
    """
    Tests for :func:`pywincffi.core.ffi.bind`
    """
    def test_no_header_provided(self):
        ffi_instance = new_ffi()

        fd, path = tempfile.mkstemp()
        self.addCleanup(self.remove, path)

        with os.fdopen(fd, "wb") as temp_stream:
            data = dedent("""
            #define HELLO_WORLD 42
            """)
            temp_stream.write(data.encode())

        with patch.object(ffi, "find_header", return_value=path) as mocked:
            kernel32 = ffi.bind(ffi_instance, "kernel32")

        mocked.assert_called_with("kernel32")
        self.assertEqual(kernel32.HELLO_WORLD, 42)

    def test_header_provided(self):
        ffi_instance = FFI()
        ffi_instance.set_unicode(True)

        header = dedent("""
        #define HELLO_WORLD 43
        """)
        kernel32 = ffi.bind(ffi_instance, "kernel32", header)
        self.assertEqual(kernel32.HELLO_WORLD, 43)


class TestHeader(TestCase):
    """
    Tests for :func:`pywincffi.core.ffi.find_header`
    """
    def test_find_header(self):
        self.assertEqual(
            join(dirname(dirname(ffi.__file__)), "headers", "kernel32.h"),
            ffi.find_header("kernel32")
        )


class TestCheckErrorCode(TestCase):
    """
    Tests for :func:`pywincffi.core.ffi.check_error_code`
    """
    def test_default_code_does_match_expected(self):
        with patch.object(ffi.ffi, "getwinerror", return_value=(0, "GTG")):
            ffi.error_check("Foobar")

    def test_default_code_does_not_match_expected(self):
        with patch.object(ffi.ffi, "getwinerror", return_value=(0, "NGTG")):
            with self.assertRaises(WindowsAPIError):
                ffi.error_check("Foobar", expected=2)

    def test_non_zero_error(self):
        with patch.object(ffi.ffi, "getwinerror", return_value=(0, "NGTG")):
            with self.assertRaises(WindowsAPIError):
                ffi.error_check("Foobar", nonzero=True)

    def test_non_zero_failure(self):
        ffi.error_check("Foobar", code=1, nonzero=True)


class TestTypeCheck(TestCase):
    """
    Tests for :func:`pywincffi.core.types.input_check`
    """
    def test_type_error(self):
        with self.assertRaises(InputError):
            ffi.input_check("foobar", 1, str)

    def test_handle_type_failure(self):
        with self.assertRaises(InputError):
            ffi.input_check("", None, "handle")

    def test_not_a_handle(self):
        typeof = Mock(kind="", cname="")
        with patch.object(ffi.ffi, "typeof", return_value=typeof):
            with self.assertRaises(InputError):
                ffi.input_check("", None, "handle")

    def test_handle_type_success(self):
        typeof = Mock(kind="pointer", cname="void *")
        with patch.object(ffi.ffi, "typeof", return_value=typeof):
            # The value does not matter here since we're
            # mocking out typeof()
            ffi.input_check("", None, "handle")