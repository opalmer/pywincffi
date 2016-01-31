"""
Exceptions
==========

Custom exceptions that ``pywincffi`` can throw.
"""

from cffi.api import CDefError


class PyWinCFFIError(Exception):
    """
    The base class for all custom exceptions that pywincffi can throw.
    """


class PyWinCFFINotImplementedError(PyWinCFFIError):
    """
    Raised if we encounter a situation where we can't figure out what
    to do.  The message for this error should contain all the information
    necessary to implement a future work around.
    """


class InputError(PyWinCFFIError):
    """
    A subclass of :class:`PyWinCFFIError` that's raised when invalid input
    is provided to a function.  Because we're passing inputs to C we have
    to be sure that the input(s) being provided are what we're expecting so
    we fail early and provide better error messages.
    """
    def __init__(  # pylint: disable=too-many-arguments
            self, name, value, expected_types, allowed_values=None, ffi=None):
        self.name = name
        self.value = value
        self.value_repr = value
        self.expected_types = expected_types
        self.allowed_values = allowed_values

        if ffi is not None:
            try:
                exceptions = (TypeError, CDefError, ffi.error)
            except AttributeError:
                exceptions = (TypeError, CDefError)

            try:
                typeof = ffi.typeof(value)
            except exceptions:
                self.value_repr = repr(value)
            else:
                self.value_repr = "%s(kind=%r, cname=%r)" % (
                    value.__class__.__name__, typeof.kind, typeof.cname)

        if self.allowed_values is None:
            self.message = "Expected type(s) %r for %s.  Got %s instead." % (
                self.expected_types, self.name, self.value_repr
            )

        else:
            self.message = \
                "Expected value for %s to be in %r. Got %s instead." % (
                    self.name, self.allowed_values, self.value_repr
                )

        super(InputError, self).__init__(self.message)


class WindowsAPIError(PyWinCFFIError):
    """
    A subclass of :class:`PyWinCFFIError` that's raised when there was a
    problem calling a Windows API function.
    """
    def __init__(self, api_function, api_error_message, code, expected_code):
        self.api_function = api_function
        self.api_error_message = api_error_message
        self.code = code
        self.expected_code = expected_code

        # We can't import the ffi module here because it would result
        # in a circular import so we exclude the two other cases such as
        # int and None.
        if not isinstance(expected_code, int) and expected_code is not None:
            self.message = \
                "Error when calling %s, error was %r.  Received " \
                "return value %s when we expected non-zero" % (
                    self.api_function, self.api_error_message, self.code
                )
        else:
            self.message = \
                "Expected a non-zero result from %r but got zero instead.  " \
                "Message from windows API was %r" % (
                    self.api_function, self.api_error_message
                )

        super(WindowsAPIError, self).__init__(self.message)


class ResourceNotFoundError(PyWinCFFIError):
    """Raised when we fail to locate a specific resource"""


class ConfigurationError(PyWinCFFIError):
    """Raised when there was a problem with the configuration file"""
