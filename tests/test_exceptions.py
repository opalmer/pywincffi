from six import PY2

from pywincffi.core import dist
from pywincffi.dev.testutil import TestCase
from pywincffi.exceptions import (
    PyWinCFFIError, InternalError, InputError, WindowsAPIError,
    PyWinCFFINotImplementedError, ResourceNotFoundError, ConfigurationError)


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

    def test_internalerror(self):
        self.assertTrue(
            issubclass(PyWinCFFINotImplementedError, InternalError))
        self.assertTrue(
            issubclass(ResourceNotFoundError, InternalError))
        self.assertTrue(
            issubclass(ConfigurationError, InternalError))


class TestInputError(TestCase):
    """
    Test case for :class:`pywincffi.exceptions.InputError`
    """
    def test_input_values_are_none(self):
        with self.assertRaises(ValueError):
            InputError(
                "", None,
                allowed_types=None, allowed_values=None, message=None)

    def test_both_allowed_values_and_types_defined(self):
        with self.assertRaises(ValueError):
            InputError("", None, allowed_types=(int, ), allowed_values=(2, ))

    def test_attribute_test_value(self):
        error = InputError("", "foo", allowed_types=(int, ))
        self.assertEqual(error.value, "foo")

    def test_attribute_allowed_types(self):
        error = InputError("", "", allowed_types=(int,))
        self.assertEqual(error.allowed_types, (int, ))

    def test_attribute_allowed_values(self):
        error = InputError("", "", allowed_values=(1,))
        self.assertEqual(error.allowed_values, (1, ))

    def test_attribute_message(self):
        error = InputError("", None, message="Foobar")
        self.assertEqual(error.message, "Foobar")

    def test_message_allowed_types_ffi_is_none(self):
        error = InputError("", None, ffi=None, allowed_types=(int, ))
        name = "type" if PY2 else "class"
        self.assertEqual(
            error.message,
            "Expected type(s) (<%s 'int'>,) for ''. Type of '' is "
            "<%s 'NoneType'>." % (name, name))

    def test_message_allowed_types_type_of_failure(self):
        ffi, _ = dist.load()
        error = InputError("", 1, ffi=ffi, allowed_types=(int,))
        name = "type" if PY2 else "class"
        self.assertEqual(
            error.message,
            "Expected type(s) (<%s 'int'>,) for ''. Type of '' is "
            "<%s 'int'>." % (name, name))

    def test_message_allowed_types_type_of_success(self):
        ffi, _ = dist.load()
        error = InputError(
            "", ffi.new("wchar_t[0]"), ffi=ffi, allowed_types=(int,))
        name = "type" if PY2 else "class"
        self.assertEqual(
            error.message,
            "Expected type(s) (<%s 'int'>,) for ''. Type of '' is "
            "CDataOwn(kind='array', cname='wchar_t[0]')." % name)


class TestWindowsAPIError(TestCase):
    """
    Test case for :class:`pywincffi.exceptions.WindowsAPIError`
    """
    def test_attribute_api_function(self):
        error = WindowsAPIError(
            "function", "there was a problem", 1, return_code=0)
        self.assertEqual(error.function, "function")

    def test_attribute_api_error_message(self):
        error = WindowsAPIError(
            "function", "there was a problem", 1, return_code=0)
        self.assertEqual(error.error, "there was a problem")

    def test_attribute_code(self):
        error = WindowsAPIError(
            "function", "there was a problem", 1, return_code=0)
        self.assertEqual(error.errno, 1)

    def test_attribute_expected_code(self):
        error = WindowsAPIError(
            "function", "there was a problem", 1, return_code=0)
        self.assertEqual(error.return_code, 0)

    def test_message_return_code_and_expected_code_is_none(self):
        error = WindowsAPIError(
            "function", "there was a problem", 1,
            return_code=None, expected_return_code=None)
        self.assertEqual(
            error.message,
            "Error when calling function. Message from Windows API was 'there "
            "was a problem' (errno: 1).")

    def test_repr(self):
        error = WindowsAPIError(
            "function", "there was a problem", 1, return_code=0,
            expected_return_code=1)
        self.assertEqual(
            repr(error),
            "WindowsAPIError('function', 'there was a problem', 1, "
            "return_code=0, expected_return_code=1)")

    def test_warning(self):
        with self.assertWarns(Warning):
            WindowsAPIError(
                "function", "there was a problem", 1, return_code="foo")
