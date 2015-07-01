"""
FFI
---

This module is mainly responsible for loading and configuring
:mod:`cffi`.  It's also responsible for some auxiliary
funcnaility as well.
"""

from pkg_resources import resource_filename

from cffi import FFI

from pywincffi.core.logger import logger
from pywincffi.exceptions import InputError, WindowsAPIError


def find_header(header_name):
    """Finds a given header for this package by name"""
    header_name = "headers/%s.h" % header_name
    logger.debug("Searching for header %r", header_name)
    return resource_filename("pywincffi", header_name)


def bind(ffi_instance, library_name, header=None):
    """
    A wrapper for :meth:`FFI.dlopen` :meth:`FFI.cdef` that
    this module uses to bin a variable to a Windows module.

    :param str library_name:
        The name of the Windows library you are attempting
        to produce a binding for, `kernel32` for example.  This
        value will be passed into :meth:`FFI.dlopen`.

    :param str header:
        The header which will be used to provide a definition
        for ``library_name``.  If not provided we'll make a call
        to :func:`find_header` using ``library_name``

    :rtype: :class:`cffi.api.FFILibrary`
    """
    if header is None:
        header_path = find_header(library_name)
        with open(header_path, "rb") as header:
            header = header.read().decode()

    ffi_instance.cdef(header)
    return ffi_instance.dlopen(library_name)


def error_check(api_function, code=None, expected=0):
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

    if code != expected:
        raise WindowsAPIError(api_function, api_error_message, code, expected)


def input_check(name, value, allowed_types):
    """
    A small wrapper around :func:`insinstance`.  This is mainly meant
    to be used inside of other functions to pre-validate input rater
    than using assertions.  It's better to fail early with bad input
    so more reasonable error message can be provided instead of from
    somewhere deep in cffi.

    :param value:
        The value we're performing the type check on

    :param allowed_types:
        The allowed type or types for ``value``

    :raises pywincffi.exceptions.InputError:
        Raised if ``value`` is not an instance of ``allowed_types``
    """
    logger.debug(
        "input_check(name=%r, value=%r, allowed_types=%r",
        name, value, allowed_types
    )
    if not isinstance(value, allowed_types):
        raise InputError(name, value, allowed_types)


def new_ffi():
    """
    Returns an instance of :class:`FFI`
    """
    ffi_instance = FFI()
    ffi_instance.set_unicode(True)
    return ffi_instance

ffi = new_ffi()
