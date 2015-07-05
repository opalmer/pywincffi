"""
FFI
---

This module is mainly responsible for loading and configuring
:mod:`cffi`.  It's also responsible for some auxiliary
funcnaility as well.
"""

from pkg_resources import resource_filename

import six
from cffi import FFI

from pywincffi.core.logger import logger
from pywincffi.exceptions import InputError, WindowsAPIError


def find_header(header_name):
    """
    Finds a header for the given ``header_name``.  Header files
    are located under the ``headers`` directory under the root
    of the pywincffi project.

    :param str header_name:
        The name of hte header to load.  (ex. kernel32)

    :returns:
        Returns the file path to the requested header.
    """
    header_name = "headers/%s.h" % header_name
    logger.debug("Searching for header %r", header_name)
    return resource_filename("pywincffi", header_name)


def bind(ffi_instance, library_name, header=None):
    """
    A wrapper for :meth:`FFI.dlopen` and :meth:`FFI.cdef`.  For
    example, to bind ``kernel32`` you could do:

    >>> from pywincffi.core.ffi import bind, ffi
    >>> kernel32 = bind(ffi, "kernel32")

    :param cffi.api.FFI ffi_instance:
        The instance of :class:`FFI` to apply the binding to.

    :param str library_name:
        The name of the Windows library you are attempting
        to produce a binding for, `kernel32` for example.  This
        value will be passed into :meth:`FFI.dlopen`.

    :keyword str header:
        An optional header to provide the definitions for the
        given ``library_name``.  This keyword is mainly used
        when testing, when not provided we contruct the header
        name using ``library_name``

    :rtype: :class:`cffi.api.FFILibrary`
    """
    if header is None:
        header_path = find_header(library_name)
        with open(header_path, "rb") as header:
            header = header.read().decode()

    ffi_instance.cdef(header)
    return ffi_instance.dlopen(library_name)


def error_check(api_function, code=None, expected=0, nonzero=False):
    """
    Checks the results of a return code against an expected result.  If
    a code is not provided we'll use :func:`ffi.getwinerror` to retrieve
    the code.

    :param str api_function:
        The Windows API function being caled.

    :raises pywincffi.exceptions.WindowsAPIError:
        Raised if we receive an unexpected result from a Windows API call
    """
    if code is None:
        code, api_error_message = ffi.getwinerror()
    else:
        code, api_error_message = ffi.getwinerror(code)

    logger.debug(
        "error_check(%r, code=%r, expected=%r)",
        api_function, code, expected
    )

    if nonzero and code != 0:
        return

    if nonzero and code == 0 or code != expected:
        raise WindowsAPIError(
            api_function, api_error_message, code, expected, nonzero=nonzero
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
    assert isinstance(name, six.string_types)

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
    assert not isinstance(allowed_types, six.string_types)

    if not isinstance(value, allowed_types):
        raise InputError(name, value, allowed_types)


def new_ffi():
    """Returns an instance of :class:`FFI`"""
    ffi_instance = FFI()
    ffi_instance.set_unicode(True)
    return ffi_instance

ffi = new_ffi()