try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

from pywincffi.core.checks import (
    INPUT_CHECK_MAPPINGS, CheckMapping, Enums, input_check, error_check)
from pywincffi.core.ffi import Library
from pywincffi.core.testutil import TestCase
from pywincffi.exceptions import WindowsAPIError, InputError


class TestCheckErrorCode(TestCase):
    """
    Tests for :func:`pywincffi.core.ffi.check_error_code`
    """
    def test_default_code_does_match_expected(self):
        ffi, _ = Library.load()

        with patch.object(ffi, "getwinerror", return_value=(0, "GTG")):
            error_check("Foobar")

    def test_default_code_does_not_match_expected(self):
        ffi, _ = Library.load()

        with patch.object(ffi, "getwinerror", return_value=(0, "NGTG")):
            with self.assertRaises(WindowsAPIError):
                error_check("Foobar", expected=2)

    def test_non_zero(self):
        ffi, _ = Library.load()

        with patch.object(ffi, "getwinerror", return_value=(1, "NGTG")):
            error_check("Foobar", expected=Enums.NON_ZERO)

    def test_non_zero_success(self):
        ffi, _ = Library.load()

        with patch.object(ffi, "getwinerror", return_value=(0, "NGTG")):
            error_check("Foobar", code=1, expected=Enums.NON_ZERO)


class TestTypeCheck(TestCase):
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
        ffi, _ = Library.load()
        typeof = Mock(kind="", cname="")
        with patch.object(ffi, "typeof", return_value=typeof):
            with self.assertRaises(InputError):
                input_check("", None, Enums.HANDLE)

    def test_handle_type_success(self):
        ffi, _ = Library.load()
        typeof = Mock(kind="pointer", cname="void *")
        with patch.object(ffi, "typeof", return_value=typeof):
            # The value does not matter here since we're
            # mocking out typeof()
            input_check("", None, Enums.HANDLE)


class TestEnumMapping(TestCase):
    def setUp(self):
        self.original_mappings = INPUT_CHECK_MAPPINGS.copy()
        INPUT_CHECK_MAPPINGS.clear()

    def tearDown(self):
        INPUT_CHECK_MAPPINGS.clear()
        INPUT_CHECK_MAPPINGS.update(self.original_mappings)

    def test_nullable(self):
        INPUT_CHECK_MAPPINGS.update(
            mapping=CheckMapping(
                kind="foo",
                cname="bar",
                nullable=True
            )
        )

        # If something is nullable but kind/cname don't match it
        # should not fail the input check
        ffi, _ = Library.load()
        typeof = Mock(kind="pointer", cname="void *")
        with patch.object(ffi, "typeof", return_value=typeof):
            input_check("", ffi.NULL, "mapping")

    def test_not_nullable(self):
        ffi, _ = Library.load()
        INPUT_CHECK_MAPPINGS.update(
            mapping=CheckMapping(
                kind="foo",
                cname="bar",
                nullable=False
            )
        )

        # If something is nullable but kind/cname don't match it
        # should not fail the input check
        typeof = Mock(kind="foo", cname="bar")
        with patch.object(ffi, "typeof", return_value=typeof):
            input_check("", ffi.NULL, "mapping")

    def test_kind_and_cname(self):
        INPUT_CHECK_MAPPINGS.update(
            mapping=CheckMapping(
                kind="foo",
                cname="bar",
                nullable=True
            )
        )

        # If something is nullable but kind/cname don't match it
        # should not fail the input check
        ffi, _ = Library.load()
        typeof = Mock(kind="foo", cname="bar")
        with patch.object(ffi, "typeof", return_value=typeof):
            input_check("", "", "mapping")


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
                "Expected value for foo to be in (2,), got 1 instead."
            )

        else:
            self.fail("InputError not raised")

    def test_assertion(self):
        with self.assertRaises(AssertionError):
            input_check("", None, allowed_values=1)
