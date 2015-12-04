"""
Checks
======

Provides functions that are responsible for internal type checks.
"""

import io
import types
from collections import namedtuple

import enum
from six import PY3, string_types

from pywincffi.core.ffi import Library
from pywincffi.core.logger import get_logger
from pywincffi.exceptions import WindowsAPIError, InputError

logger = get_logger("core.check")

NoneType = type(None)
Enums = enum.Enum("Enums", """
NON_ZERO
HANDLE
UTF8
OVERLAPPED
PYFILE
""".strip())

if PY3:
    FileType = io.IOBase
else:
    FileType = types.FileType  # pylint: disable=no-member

# A mapping of value we can expect to get from `ffi.typeof` against
# some known input enums.
CheckMapping = namedtuple("CheckMapping", ("kind", "cname", "nullable"))
INPUT_CHECK_MAPPINGS = {
    Enums.HANDLE: CheckMapping(
        kind="pointer",
        cname="void *",
        nullable=False
    ),
    Enums.OVERLAPPED: CheckMapping(
        kind="array",
        cname="OVERLAPPED[1]",
        nullable=True
    )
}


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
        call.  This can also be passed ``pywincffi.core.checks.Enums.NON_ZERO``
        if ``code`` can be anything but zero.

    :raises pywincffi.exceptions.WindowsAPIError:
        Raised if we receive an unexpected result from a Windows API call
    """
    ffi, _ = Library.load()

    if code is None:
        result, api_error_message = ffi.getwinerror()
    else:
        # If the is zero and we expected non-zero then
        # the real error message can be found with ffi.getwinerror.
        if code == 0 and expected is Enums.NON_ZERO:
            result = code
            _, api_error_message = ffi.getwinerror()
        else:
            result, api_error_message = ffi.getwinerror(code)

    logger.debug(
        "error_check(%r, code=%r, result=%r, expected=%r)",
        api_function, code, result, expected
    )

    if (expected is Enums.NON_ZERO and (
            result != 0 or code is not None and code != 0)):
        return

    if expected != result:
        raise WindowsAPIError(
            api_function, api_error_message, result, expected
        )


def input_check(name, value, allowed_types=None, allowed_values=None):
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
        also supports a special value, ``pywincffi.core.checks.Enums.HANDLE``,
        which will check to ensure ``value`` is a handle object.

    :param tuple allowed_values:
        A tuple of allowed values.  When provided ``value`` must
        be in this tuple otherwise :class:`InputError` will be
        raised.

    :raises pywincffi.exceptions.InputError:
        Raised if ``value`` is not an instance of ``allowed_types``
    """
    assert isinstance(name, string_types)
    assert allowed_values is None or isinstance(allowed_values, tuple)
    ffi, _ = Library.load()

    logger.debug(
        "input_check(name=%r, value=%r, allowed_types=%r, allowed_values=%r",
        name, value, allowed_types, allowed_values
    )

    if allowed_types is None and isinstance(allowed_values, tuple):
        if value not in allowed_values:
            raise InputError(
                name, value, allowed_types, allowed_values=allowed_values)

    elif allowed_types in INPUT_CHECK_MAPPINGS:
        mapping = INPUT_CHECK_MAPPINGS[allowed_types]

        try:
            typeof = ffi.typeof(value)

            if mapping.nullable and value is ffi.NULL:
                return

            if typeof.kind != mapping.kind or typeof.cname != mapping.cname:
                raise TypeError

        except TypeError:
            raise InputError(name, value, allowed_types)

    elif allowed_types is Enums.UTF8:
        try:
            value.encode("utf-8")
        except (ValueError, AttributeError):
            raise InputError(name, value, allowed_types)

    elif allowed_types is Enums.PYFILE:
        if not isinstance(value, FileType):
            raise InputError(name, value, "file type")

    else:
        if not isinstance(value, allowed_types):
            raise InputError(name, value, allowed_types)
