"""
FFI
---

This module is mainly responsible for loading and configuring
:mod:`cffi`.
"""

from errno import ENOENT
from os.path import join

from cffi import FFI
from pkg_resources import resource_filename

from pywincffi.core.logger import get_logger
from pywincffi.exceptions import ResourceNotFoundError

# To keep lint on non-windows platforms happy.
try:
    WindowsError
except NameError:
    WindowsError = OSError


logger = get_logger("core.ffi")


class Library(object):  # pylint: disable=too-few-public-methods
    """
    A wrapper around :meth:`FFI.cdef` and :meth:`FFI.dlopen` that
    also performs caching.  Without caching a library could be
    loaded multiple times causing an exception to be raised when
    a function is redefined.
    """
    CACHE = (None, None)
    VERIFY_LIBRARIES = ("kernel32", )
    HEADERS_ROOT = resource_filename(
        "pywincffi", join("core", "cdefs", "headers"))
    SOURCES_ROOT = resource_filename(
        "pywincffi", join("core", "cdefs", "sources"))
    HEADERS = (
        join(HEADERS_ROOT, "constants.h"),
        join(HEADERS_ROOT, "structs.h"),
        join(HEADERS_ROOT, "functions.h")
    )
    SOURCES = (
        join(SOURCES_ROOT, "main.c"),
    )

    @staticmethod
    def _load_files(filepaths):
        """
        Given a tuple of file paths open each file and return a string
        containing the contents of all the files loaded.

        :param tuple filepaths:
            A tuple of file paths to load

        :raises ResourceNotFoundError:
            Raised if one of the paths in ``filepaths`` could not
            be loaded.

        :return:
            Returns a string containing all the loaded paths.
        """
        output = ""

        for path in filepaths:
            logger.debug("Reading %s", path)
            try:
                with open(path, "r") as open_file:
                    output += open_file.read()

            except (OSError, IOError, WindowsError) as error:
                if error.errno == ENOENT:
                    raise ResourceNotFoundError("Failed to locate %s" % path)

        return output

    @classmethod
    def load(cls):
        """
        Main function which loads up an instance of the library.

        :returns:
            Returns a tuple of :class:`FFI` and the loaded library.
        """
        if cls.CACHE[0] is not None:
            return cls.CACHE

        # Read in headers
        csource = cls._load_files(cls.HEADERS)
        source = cls._load_files(cls.SOURCES)

        # Compile
        # TODO: this should do something slightly different if pre-compiled
        ffi = FFI()
        ffi.set_unicode(True)
        ffi.cdef(csource)
        library = ffi.verify(source, libraries=cls.VERIFY_LIBRARIES)

        cls.CACHE = (ffi, library)

        return cls.CACHE
