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


class InputError(PyWinCFFIError):
    """
    A subclass of :class:`PyWinCFFIError` that's raised when invalid input
    is provided to a function.  Because we're passing inputs to C we have
    to be sure that the input(s) being provided are what we're expecting so
    we fail early and provide better error messages.


    :param str name:
        The name of the parameter being checked.

    :param value:
        The value of the parameter being checked.

    :keyword allowed_types:
        The expected type(s). If provided then the exception's message will
        be tailored to provide information about ``value``'s type and the
        possible input types.

    :keyword allowed_values:
        The expected value(s).  If provided then the exception's message will
        be tailored to provide information about what value(s) were allowed
        for ``value``.

    :keyword ffi:
        If ``value`` is a C object, ``ffi`` is provided and ``allowed_types``
        is provided as well then the provided ``ffi`` instance will be used
        to provide additional context.

    :keyword str message:
        A custom error message.  This will override the default error messages
        which :class:`InputError` would normally generate.  This can be
        helpful if there is a problem with a given input parameter to a
        function but it's unrelated to the type of input.
    """
    def __init__(  # pylint: disable=too-many-arguments
            self, name, value,
            allowed_types=None, allowed_values=None, ffi=None, message=None):
        if allowed_types is not None and allowed_values is not None:
            raise ValueError(
                "Please provide either `allowed_types` or `allowed_values`")

        if (allowed_types is None and allowed_values is None and
                message is None):
            raise ValueError(
                "Please provide `allowed_types`, `allowed_values` or "
                "`message`")

        self.name = name
        self.value = value
        self.allowed_types = allowed_types
        self.allowed_values = allowed_values
        self.message = message

        if self.message is None and self.allowed_types is not None:
            if ffi is None:
                typeof = repr(type(value))
            else:
                try:
                    ffi_exceptions = (TypeError, CDefError, ffi.error)
                except AttributeError:  # pragma: no cover
                    ffi_exceptions = (TypeError, CDefError)

                try:
                    typeof = ffi.typeof(value)
                except ffi_exceptions:
                    typeof = repr(type(value))
                else:
                    typeof = "{classname}(kind={kind}, cname={cname})".format(
                        classname=value.__class__.__name__,
                        kind=repr(typeof.kind), cname=repr(typeof.cname))

            self.message = \
                "Expected type(s) {expected} for {name}. Type of {name} " \
                "is {typeof}.".format(
                    expected=repr(allowed_types), name=repr(name),
                    typeof=typeof)

        elif self.message is None and self.allowed_values is not None:
            self.message = \
                "Expected the value of {name} to be in {values}. Value of " \
                "{name} is {value}.".format(
                    name=repr(name), values=allowed_values, value=repr(value))

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
    # pylint: disable=too-many-arguments
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


class InternalError(PyWinCFFIError):
    """
    Raised if we encounter an internal error.  Most likely this is an
    indication of a bug in pywincffi but it could also be a problem caused by
    an unexpected use case.
    """


class PyWinCFFINotImplementedError(InternalError):
    """
    Raised if we encounter a situation where we can't figure out what
    to do.  The message for this error should contain all the information
    necessary to implement a future work around.
    """


class ResourceNotFoundError(InternalError):
    """Raised when we fail to locate a specific resource"""


class ConfigurationError(InternalError):
    """Raised when there was a problem with the configuration file"""
