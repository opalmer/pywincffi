"""
Library
-------

This module is responsible for loading and configuraing
:mod:`cffi`.
"""

from cffi import FFI

ffi = FFI()
ffi.set_unicode(True)


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
        ffi_.cdef(header.read())

    return ffi_.dlopen(library_name)


