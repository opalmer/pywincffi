"""
FFI
---

This module is mainly responsible for loading and configuring
:mod:`cffi`.
"""

from errno import ENOENT

from cffi import FFI
from pkg_resources import resource_filename

from pywincffi.core.logger import get_logger
from pywincffi.exceptions import HeaderNotFoundError


logger = get_logger("core.ffi")


class Library(object):
    """
    A wrapper around :meth:`FFI.cdef` and :meth:`FFI.dlopen` that
    also performs caching.  Without caching a library could be
    loaded multiple times causing an exception to be raised when
    a function is redefined.
    """
    CACHE = {}

    @staticmethod
    def _load_header(header_name):
        """
        For the given ``header_name`` locate the path on disk and
        attempt to load it.  This function will search the `headers`
        directory under the root of the pywincffi project.

        :param str header_name:
            The name of the header to load, kernel32.h for example.  This
            will be passed along to :func:`resource_filename` to construct
            the path.

        :returns:
            Returns the loaded header file or ``None`` if no header for
            for the given name could be found.
        """
        header_name = "headers/" + header_name
        logger.debug("Searching for header %r", header_name)
        path = resource_filename("pywincffi", header_name)

        logger.debug("Loading header for %s from %s", header_name, path)

        try:
            with open(path, "rb") as stream:
                header_data = stream.read().decode()
        except (OSError, IOError, WindowsError) as error:
            if error.errno == ENOENT:
                logger.error("No such header %s", path)
                return None
            raise
        return header_data

    @classmethod
    def load(cls, library_name, ffi_instance=None, header=None):
        """
        Loads the given ``library_name`` and returns a bound instance of
        :class:`FFI`.  The return value may either a new instance or
        a cached result we've seen before.

        :param str library_name:
            The name of the library to load (ex. kernel32)

        :keyword cffi.api.FFI ffi_instance:
            The optional instance of :class:`FFI` to bind to.  If no value
            is provided we'll use the global ``pywincffi.core.ffi.ffi`
            instance instead.

        :keyword str header:
            An optional header to provide the definitions for the
            given ``library_name``.  This keyword is mainly used
            when testing and when not provided we use :meth:`_find_header`
            to locate the path to the header file for the given
            library_name.
        """
        if ffi_instance is None:
            ffi_instance = ffi

        cached = cls.CACHE.get(ffi_instance, None)
        if cached is not None and library_name in cached:
            logger.debug(
                "Returning cached library %s for %s",
                library_name, ffi_instance
            )
            return cached[library_name]

        logger.debug("Loading %s onto %s", library_name, ffi_instance)

        if header is None:
            header = cls._load_header(library_name + ".h")

        if header is None:
            raise HeaderNotFoundError(
                "Failed to locate header for %s" % library_name
            )

        ffi_instance.cdef(header)
        library = ffi_instance.dlopen(library_name)
        instance_cache = cls.CACHE.setdefault(ffi_instance, {})
        instance_cache[library_name] = library
        return library


def new_ffi():
    """Returns an instance of :class:`FFI`"""
    ffi_instance = FFI()
    ffi_instance.set_unicode(True)
    return ffi_instance

ffi = new_ffi()
