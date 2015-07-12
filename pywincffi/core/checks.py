from collections import namedtuple

from six import string_types

from pywincffi.core.ffi import ffi
from pywincffi.core.logger import logger
from pywincffi.exceptions import WindowsAPIError, InputError

logger = logger.getChild("core.check")
_Enums = namedtuple("_Enums", ("NON_ZERO", ))
Enums = _Enums(
    NON_ZERO=object()
)


def error_check(api_function, code=None, expected=0):
    """
    Checks the results of a return code against an expected result.  If
    a code is not provided we'll use :func:`ffi.getwinerror` to retrieve
    the code.

    :param str api_function:
        The Windows API function being called.

    :param int code:
        An explicit code to compare against.  This can be used
        instead of asking :func:`ffi.getwinerrro` to retrieve a code.

    :param int expected:
        The code we expect to have as a result of a successful
        call.  This can also be passed ``pywincffi.ffi.NON_ZERO`` if
        ``code`` can be anything but zero.

    :raises pywincffi.exceptions.WindowsAPIError:
        Raised if we receive an unexpected result from a Windows API call
    """
    if code is None:
        result, api_error_message = ffi.getwinerror()
    else:
        result, api_error_message = ffi.getwinerror(code)

    expected_str = expected
    if expected is Enums.NON_ZERO:
        expected_str = "non-zero"

    logger.debug(
        "error_check(%r, code=%r, result=%r, expected=%r)",
        api_function, code, result, expected_str
    )

    if (expected is Enums.NON_ZERO
        and (result != 0 or code is not None and code != 0)):
        return

    if expected != result:
        raise WindowsAPIError(
            api_function, api_error_message, result, expected
        )


def input_check(name, value, allowed_types):
    """
    A small wrapper around :func:`isinstance`.  This is mainly meant
    to be used inside of other functions to pre-validate input rater
    than using assertions.  It's better to fail early with bad input
    so more reasonable error message can be provided instead of from
    somewhere deep in cffi or Windows.

    :param str name:
        The name of the input being checked.  This is provided
        so error messages make more sense and can be attributed
        to specific input arguments.

    :param value:
        The value we're performing the type check on.

    :param allowed_types:
        The allowed type or types for ``value``.  This argument
        also supports a string for `allowed_types` called 'handle'
        to validate ctype handle declarations.

    :raises pywincffi.exceptions.InputError:
        Raised if ``value`` is not an instance of ``allowed_types``
    """
    assert isinstance(name, string_types)

    logger.debug(
        "input_check(name=%r, value=%r, allowed_types=%r",
        name, value, allowed_types
    )
    if allowed_types == "handle":
        try:
            typeof = ffi.typeof(value)
            if typeof.kind != "pointer" or typeof.cname != "void *":
                raise TypeError

        except TypeError:
            raise InputError(name, value, allowed_types)

        return

    # A new named type was provided for `allowed_types`,
    # be sure to update the docs for `allowed_types`
    assert not isinstance(allowed_types, string_types)

    if not isinstance(value, allowed_types):
        raise InputError(name, value, allowed_types)
