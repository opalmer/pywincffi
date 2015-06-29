"""
Core
----

This module is responsible for loading and configuring access
to the Windows API.
"""

from pkg_resources import resource_filename
from cffi import FFI


def find_header(header_name):
    """Finds a given header for this package by name"""
    return resource_filename("pywincffi", "headers/%s.h" % header_name)


def bind(library_name, header_path, ffi_=None):
    """
    A wrapper for :meth:`FFI.dlopen` :meth:`FFI.cdef` that
    this module uses to bin a variable to a Windows module.

    :param str library_name:
        The name of the Windows library you are attempting
        to produce a binding for, `kernel32` for example.  This
        value will be passed into :meth:`FFI.dlopen`.

    :param str header_path:
        The path to the header file which is used to declare
        symbols for the given library.  This value will be
        passed into :meth:`FFI.cdef`.

    :rtype: :class:`cffi.api.FFILibrary`
    """
    if ffi_ is None:
        ffi_ = ffi

    with open(header_path, "rb") as header:
        ffi_.cdef(header.read().decode())

    return ffi_.dlopen(library_name)


ffi = FFI()
ffi.set_unicode(True)
