"""
Exceptions
==========

Custom exceptions that ``pywincffi`` can throw.
"""

import warnings

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

    :param str function:
        The Windows API function being called when the error was raised.

    :param str error:
        A string representation of the error message.

    :param int errno:
        An integer representing the error.  This usually represents
        a constant which Windows has produced in response to a problem.

    :keyword int return_code:
        If the return value of a function has been checked the resulting
        code will be set as this value.

    :keyword int expected_return_code:
        The value we expected to receive for ``code``.
    """
    def __init__(self, function, error, errno,
                 return_code=None, expected_return_code=None):
        self.function = function
        self.error = error
        self.errno = errno
        self.return_code = return_code
        self.expected_return_code = expected_return_code

        if return_code is None and expected_return_code is None:
            self.message = \
                "Error when calling %s. Message from Windows API was " \
                "%r (errno: %s)." % (self.function, self.error, errno)

        elif return_code is not None and expected_return_code is not None:
            self.message = (
                "Error when calling %s.  Expected to receive %r from %s "
                "but got %r instead." % (
                    self.function, self.return_code, self.function,
                    self.expected_return_code
                )
            )

        # Generic implementation which we should probably handle
        # better so throw a warning.
        else:  # pragma: no cover
            warnings.warn(Warning(), "Pre-formatting not available")
            self.message = (
                "Error when calling %s. (error: %s, errno: %s, "
                "return_code: %r, expected_return_code: %r)" % (
                    self.function, self.error, self.errno, self.return_code,
                    self.expected_return_code
                )
            )

        super(WindowsAPIError, self).__init__(self.message)

    def __repr__(self):
        return "%s(%r, %r, %r, return_code=%r, expected_return_code=%r)" % (
            self.__class__.__name__, self.function, self.error, self.errno,
            self.return_code, self.expected_return_code
        )

class ResourceNotFoundError(PyWinCFFIError):
    """Raised when we fail to locate a specific resource"""


class ConfigurationError(PyWinCFFIError):
    """Raised when there was a problem with the configuration file"""
