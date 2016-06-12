from pywincffi.dev.testutil import TestCase
from pywincffi.exceptions import (
    PyWinCFFIError, InputError, WindowsAPIError, PyWinCFFINotImplementedError)


class TestBaseClasses(TestCase):
    """
    Tests the base classes of our custom exceptions
    """
    def test_pywincffierror(self):
        self.assertTrue(issubclass(PyWinCFFIError, Exception))

    def test_inputerror(self):
        self.assertTrue(issubclass(InputError, PyWinCFFIError))

    def test_windowsapierror(self):
        self.assertTrue(issubclass(WindowsAPIError, PyWinCFFIError))

    def test_notimplementederror(self):
        self.assertTrue(
            issubclass(PyWinCFFINotImplementedError, PyWinCFFIError))


class TestInputError(TestCase):
    """
    Test case for :class:`pywincffi.exceptions.InputError`
    """
    def test_ivar_name(self):
        error = InputError("name", "value", (str, int))
        self.assertEqual(error.name, "name")

    def test_ivar_value(self):
        error = InputError("name", "value", (str, int))
        self.assertEqual(error.value, "value")

    def test_ivar_expected_types(self):
        error = InputError("name", "value", (str, int))
        self.assertEqual(error.expected_types, (str, int))

    def test_str(self):
        error = InputError("name", "value", (str, int))
        self.assertEqual(str(error), error.message)

    def test_custom_message(self):
        error = InputError(
            "name", "value", (str, int), message="Hello, world.")
        self.assertEqual(str(error), "Hello, world.")


class TestWindowsAPIError(TestCase):
    """
    Test case for :class:`pywincffi.exceptions.WindowsAPIError`
    """
    def test_ivar_api_function(self):
        error = WindowsAPIError(
            "function", "there was a problem", 1, return_code=0)
        self.assertEqual(error.function, "function")

    def test_ivar_api_error_message(self):
        error = WindowsAPIError(
            "function", "there was a problem", 1, return_code=0)
        self.assertEqual(error.error, "there was a problem")

    def test_ivar_code(self):
        error = WindowsAPIError(
            "function", "there was a problem", 1, return_code=0)
        self.assertEqual(error.errno, 1)

    def test_ivar_expected_code(self):
        error = WindowsAPIError(
            "function", "there was a problem", 1, return_code=0)
        self.assertEqual(error.return_code, 0)

    def test_repr(self):
        error = WindowsAPIError(
            "function", "there was a problem", 1, return_code=0,
            expected_return_code=1)
        self.assertEqual(
            repr(error),
            "WindowsAPIError('function', 'there was a problem', 1, "
            "return_code=0, expected_return_code=1)"
        )

    def test_warning(self):

        with self.assertWarns(Warning):
            WindowsAPIError(
                "function", "there was a problem", 1, return_code="foo")
