from pywincffi.core.checks import input_check
from pywincffi.dev.testutil import TestCase
from pywincffi.exceptions import InputError


class TestTypeCheckFailure(TestCase):
    """
    Tests for :func:`pywincffi.core.types.input_check`
    """
    def test_type_error(self):
        with self.assertRaises(InputError):
            input_check("foobar", 1, str)

    def test_handle_type_failure(self):
        with self.assertRaises(InputError):
            input_check("", None, type(int))


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
