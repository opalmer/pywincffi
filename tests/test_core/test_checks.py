import io
import os
import tempfile
import types

from six import PY3, PY2
from mock import patch
from cffi import FFI

from pywincffi.core import dist
from pywincffi.core.checks import (
    INPUT_CHECK_MAPPINGS, FileType, CheckMapping, Enums,
    input_check, error_check)
from pywincffi.core.config import config
from pywincffi.core.testutil import TestCase
from pywincffi.exceptions import WindowsAPIError, InputError


# TODO: rewrite this so it works for both precompiled and inline modules
class TestCheckErrorCode(TestCase):
    """
    Tests for :func:`pywincffi.core.ffi.check_error_code`
    """
    LIBRARY_MODE = "inline"

    def setUp(self):
        super(TestCheckErrorCode, self).setUp()
        if config.precompiled():
            self.skipTest("inline only")

        # TODO: build inline here, replace dist.load()

    def test_default_code_does_match_expected(self):
        with patch.object(FFI, "getwinerror", return_value=(0, "GTG")):
            error_check("Foobar")

    def test_default_code_does_not_match_expected(self):
        with patch.object(FFI, "getwinerror", return_value=(0, "NGTG")):
            with self.assertRaises(WindowsAPIError):
                error_check("Foobar", expected=2)

    def test_non_zero(self):
        with patch.object(FFI, "getwinerror", return_value=(1, "NGTG")):
            error_check("Foobar", expected=Enums.NON_ZERO)

    def test_non_zero_success(self):
        with patch.object(FFI, "getwinerror", return_value=(0, "NGTG")):
            error_check("Foobar", code=1, expected=Enums.NON_ZERO)


class TestTypeCheckFailure(TestCase):
    """
    Tests for :func:`pywincffi.core.types.input_check`
    """
    def test_type_error(self):
        with self.assertRaises(InputError):
            input_check("foobar", 1, str)

    def test_handle_type_failure(self):
        with self.assertRaises(InputError):
            input_check("", None, Enums.HANDLE)

    def test_not_a_handle(self):
        ffi, _ = dist.load()
        with self.assertRaises(InputError):
            input_check("", ffi.new("void *[2]"), Enums.HANDLE)


class TestEnumMapping(TestCase):
    def setUp(self):
        self.original_mappings = INPUT_CHECK_MAPPINGS.copy()

    def tearDown(self):
        super(TestEnumMapping, self).tearDown()
        INPUT_CHECK_MAPPINGS.clear()
        INPUT_CHECK_MAPPINGS.update(self.original_mappings)

    def test_nullable(self):
        INPUT_CHECK_MAPPINGS.update(
            mapping=CheckMapping(
                kind="pointer",
                cname="void *",
                nullable=True
            )
        )

        ffi, _ = dist.load()
        input_check("", ffi.NULL, "mapping")

    def test_overlapped(self):
        ffi, _ = dist.load()
        input_check("", ffi.new("OVERLAPPED[1]"), Enums.OVERLAPPED)


class TestEnumUTF8(TestCase):
    def test_attribute_error(self):
        with self.assertRaises(InputError):
            input_check("", None, Enums.UTF8)


class TestAllowedValues(TestCase):
    def test_exception_attribute(self):
        try:
            input_check("", 1, allowed_values=(2, ))

        except InputError as error:
            self.assertEqual(error.allowed_values, (2, ))

        else:
            self.fail("InputError not raised")

    def test_valid(self):
        input_check("", 1, allowed_values=(1, ))

    def test_invalid(self):
        with self.assertRaises(InputError):
            input_check("", 1, allowed_values=(2, ))

    def test_invalid_message(self):
        try:
            input_check("foo", 1, allowed_values=(2, ))

        except InputError as error:
            self.assertEqual(
                error.message,
                "Expected value for foo to be in (2,). Got 1 instead."
            )

        else:
            self.fail("InputError not raised")

    def test_assertion(self):
        with self.assertRaises(AssertionError):
            input_check("", None, allowed_values=1)


class TestEnumPyFile(TestCase):
    def test_file_type(self):
        if PY3:
            self.assertIs(FileType, io.IOBase)
        elif PY2:
            # pylint: disable=no-member
            self.assertIs(FileType, types.FileType)
        else:
            self.fail("This is neither Python 2 or 3")

    def test_valid(self):
        fd, path = tempfile.mkstemp()
        self.addCleanup(os.remove, path)

        with os.fdopen(fd, "r") as python_file:
            input_check("", python_file, Enums.PYFILE)

    def test_invalid(self):
        fd, path = tempfile.mkstemp()
        os.close(fd)
        self.addCleanup(os.remove, path)

        with self.assertRaises(InputError):
            input_check("", path, Enums.PYFILE)
