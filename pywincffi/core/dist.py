"""
Distribution
============

Module responsible for building the pywincffi distribution
in ``setup.py``.  This module is meant to serve two
purposes.  The first is to serve as the main means of loading
the pywincffi library:

>>> from pywincffi.core import dist
>>> ffi, lib = dist.load()

The second is to facilitate a means of building a static
library.  This is used by the setup.py during the install
process to build and install pywincffi as well as a wheel
for distribution.

The reason for this setup is so that pywincffi can handle
the underlying load process inline. This makes it easier to
test as well as perform some additional testing/development
on non-windows platforms.
"""

from collections import namedtuple
from os.path import join, isfile
from pkg_resources import resource_filename

from cffi import FFI

from pywincffi.core.config import config
from pywincffi.core.logger import get_logger
from pywincffi.exceptions import ResourceNotFoundError


logger = get_logger("core.dist")
InlineModule = namedtuple("InlineModule", ("ffi", "lib"))


def get_filepath(root, filename):
    """
    Returns the filepath to the requested header or source
    file.

    :param str root:
        The root directory under ``pywincffi/core/cdefs``. 'headers'
        for example would be a valid entry here.

    :param str filename:
        The name of the file you want to retrieve under ``root``.

    :raises ResourceNotFoundError:
        Raised if the function could not find the requested file.
    """
    logger.debug("get_filepath(%r, %r)", root, filename)
    path = resource_filename(
        "pywincffi", join("core", "cdefs", root, filename))

    if not isfile(path):
        raise ResourceNotFoundError(
            "Failed to locate %s/%s" % (root, filename))

    return path


class Distribution(object):
    """
    A class responsible for building, caching and returning
    the built artifacts for :mod:`pywincffi`

    :ivar str MODULE_NAME:
        The name of the module to pass to :meth:`FFI.set_source`. This
        will eventually end up becoming the name of the underlying C-module
        that is built.

    :ivar tuple HEADERS:
        A tuple containing all the headers used to build pywincffi.

    :ivar tuple SOURCES:
        A tuple containing all the C source files to build pywincffi.

    :ivar tuple LIBRARIES:
        A tuple of Windows library names that :meth:`FFI.verify` should
        use.
    """
    MODULE_NAME = "_pywincffi"
    HEADERS = (
        get_filepath("headers", "constants.h"),
        get_filepath("headers", "structs.h"),
        get_filepath("headers", "functions.h")
    )
    SOURCES = (get_filepath("sources", "main.c"), )
    LIBRARIES = ("kernel32", )

    # Attributes used internally by this class for caching.
    _pywincffi = None

    @classmethod
    def load_definitions(cls):
        """
        Reads in the headers and source files and produces
        a tuple of strings with the results.

        :rtype: tuple
        :return:
            Returns a tuple of strings containing the headers
            and sources.
        """
        header = ""
        source = ""

        for path in cls.HEADERS:
            logger.debug("Reading %s", path)
            with open(path, "r") as file_:
                header += file_.read()

        for path in cls.SOURCES:
            logger.debug("Reading %s", path)
            with open(path, "r") as file_:
                source += file_.read()

        return header, source

    @classmethod
    def inline(cls):
        """
        Compiles pywincffi in inline mode.  This is mainly used when
        doing development and is conditionally called by :meth:`load`
        below.
        """
        logger.debug("Compiling inline")
        header, source = cls.load_definitions()

        ffi_class = FFI()
        ffi_class.set_unicode(True)
        ffi_class.cdef(header)
        cls._pywincffi = InlineModule(
            ffi=ffi_class,
            lib=ffi_class.verify(source, libraries=cls.LIBRARIES)
        )

        return cls._pywincffi.ffi, cls._pywincffi.lib

    @classmethod
    def out_of_line(cls, compile_=True):
        """
        Compiles pywincffi in out of line mode.  This is used to create a
        distribution of pywcinffi and more specifically is used by
        ``setup.py``.

        :param bool compile_:
            If True then perform the compile step as well.  By default calling
            this executes :func:`FFI.compile` which will build the underlying
            library.

        :returns:
            Returns a tuple of elements containing an instance of
            :class:`FFI` and a string pointing at the module that
            was built.
        """
        header, source = cls.load_definitions()

        ffi_class = FFI()
        ffi_class.set_unicode(True)
        ffi_class.set_source(cls.MODULE_NAME, source)
        ffi_class.cdef(header)

        built_path = None
        if compile_:
            tempdir = config.tempdir()
            logger.debug("Compiling out of line to %s", tempdir)
            built_path = ffi_class.compile(tmpdir=tempdir)

        return ffi_class, built_path

    @classmethod
    def load(cls):
        """
        Responsible for loading an instance of :class:`FFI` and
        the underlying compiled library.  This class method will
        have different behaviors depending on a few factors:

            * If ``PYWINCFFI_DEV`` is set to ``1`` in the environment
              we call and return :meth:`inline`.
            * Attempt to load :mod:`pywincffi._pywincffi`.  If we can,
              instance :class:`FFI` and return this plus
              :mod:`pywincffi._pywincffi`.
            * If :mod:`pywincffi._pywincffi` can't be loaded, call
              :meth:`inline` to try and compile the module instead.
        """
        if not config.precompiled():
            return cls.inline()

        # Return the pre-cached library if we've
        # already loaded one below.
        if cls._pywincffi is not None:
            return cls._pywincffi.ffi, cls._pywincffi.lib

        try:
            import _pywincffi
            cls._pywincffi = _pywincffi
            return cls._pywincffi.ffi, cls._pywincffi.lib

        except ImportError:
            logger.warning(
                "Failed to load _pywincffi, attempting to compile inline.")
            return cls.inline()


def ffi():
    """
    Called by the setup.py to get an out of line instance of :class:`FFI`
    which can be used to build pywincffi.
    """
    return Distribution.out_of_line(compile_=False)[0]


def load():
    """
    The main function used by pywincffi to load an instance of
    :class:`FFI` and the underlying build library.
    """
    return Distribution.load()

__all__ = ("ffi", "load")
