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
"""

import re
import shutil
import tempfile
from errno import ENOENT
from os.path import join, isfile
from pkg_resources import resource_filename

from cffi import FFI

from pywincffi.core.logger import get_logger
from pywincffi.exceptions import ResourceNotFoundError, InternalError

imp = None  # pylint: disable=invalid-name
ExtensionFileLoader = None  # pylint: disable=invalid-name
try:
    # pylint: disable=wrong-import-order,wrong-import-position
    from importlib.machinery import ExtensionFileLoader
except ImportError:  # pragma: no cover
    import imp  # pylint: disable=wrong-import-position,wrong-import-order


try:
    WindowsError
except NameError:  # pragma: no cover
    WindowsError = OSError  # pylint: disable=redefined-builtin

__all__ = ("load", )

logger = get_logger("core.dist")

MODULE_NAME = "_pywincffi"
HEADER_FILES = (
    resource_filename(
        "pywincffi", join("core", "cdefs", "headers", "typedefs.h")),
    resource_filename(
        "pywincffi", join("core", "cdefs", "headers", "constants.h")),
    resource_filename(
        "pywincffi", join("core", "cdefs", "headers", "structs.h")),
    resource_filename(
        "pywincffi", join("core", "cdefs", "headers", "functions.h")))
SOURCE_FILES = (
    resource_filename(
        "pywincffi", join("core", "cdefs", "sources", "main.c")), )
LIBRARIES = ("kernel32", "user32", "Ws2_32")
REGEX_SAL_ANNOTATION = re.compile(
    r"\b(_In_|_Inout_|_Out_|_Outptr_|_Reserved_)(opt_)?\b")


class LibraryWrapper(object):  # pylint: disable=too-few-public-methods
    """
    Because of differences between Windows versions and some issues with cffi
    we need to wrap the library that cffi produces.  Without this certain
    constants can't be included in the lib, such as INVALID_HANDLE_VALUE which
    has a negative value.  Other constants, such as FILE_FLAG_SESSION_AWARE,
    are not available on all Windows versions so this class helps to provide
    a uniform interface.

    .. warning::

        Please do not define constants here unless absolutely necessary.  By
        default, constants should be defined in
        :blob:`pywincffi/core/cdefs/headers/constants.h` unless some conditions
        are met:
            * cffi cannot compile the requested constant.
            * The constant is only defined in a few Windows SDK versions and
              it can't be conditionally defined in main.c.
    """
    _RUNTIME_CONSTANTS = dict(
        # Defined here because cffi can't handle negative values
        # in constants yet.
        INVALID_HANDLE_VALUE=-1
    )

    def __init__(self, library):
        self._library = library

    def __dir__(self):
        """
        Overrides the default ``__dir__`` function so functions such as
        :func:`dir` return the attributes of the underlying library plus
        the runtime constants.
        """
        return dir(self._library) + list(self._RUNTIME_CONSTANTS.keys())

    def __getattribute__(self, item):
        """
        Overrides the default ``__getattribute__`` function so that we
        can provide more useful results for certain attributes.
        """
        if item == "__dict__":
            library_dict = self._library.__dict__.copy()
            library_dict.update(self._RUNTIME_CONSTANTS)
            return library_dict

        return object.__getattribute__(self, item)

    def __getattr__(self, item):
        """
        Attempts to retrieve the requested attribute.  This will first look
        for the attribute on the library we're wrapping then try to look
        for a runtime constant defined on this class.
        """
        # Most likely we're looking for an attribute on the
        # compiled library.
        try:
            return getattr(self._library, item)
        except AttributeError as initial_exception:
            # Maybe it's a predefined constant?
            try:
                return self._RUNTIME_CONSTANTS[item]
            except KeyError:
                pass

            # It's not an attribute in either the library or the
            # runtime constants so it shouldn't exist.
            raise initial_exception

    def __repr__(self):  # pragma: no cover
        return "%s(%r)" % (self.__class__.__name__, self._library)


class Loader(object):
    """
    A class which provides a cache for :func:`load`.
    """
    cache = None

    @classmethod
    def set(cls, ffi, library):
        """
        Establishes the cache.

        :raises pywincffi.exceptions.InternalError:
            Raised if the cache was already setup once.
        """
        if cls.cache is not None:
            # Setting up the cache multiple times is an indication of a
            # possible bug.
            raise InternalError("The cache has already been established")

        cls.cache = (ffi, library)

    @classmethod
    def get(cls):
        """
        Retrieves the current cache.

        :raises pywincffi.exceptions.InternalError:
            Raised if an attempt is made to retrieve the cache when it
            has not been setup yet.
        """
        if cls.cache is None:
            raise InternalError("The cache has not been established yet")
        return cls.cache


def _import_path(path, module_name=MODULE_NAME):
    """
    Function which imports ``path`` and returns it as a module.  This is
    meant to import pyd files produced by :meth:`Distribution._build` in
    a Python 2/3 agnostic fashion.

    :param str path:
        The path to the file to import

    :keyword str module_name:
        Optional name of the module being imported.  By default
        this will use ``_pywincffi`` if no value is provided.

    :raises ResourceNotFoundError:
        Raised if ``path`` does not exist.
    """
    logger.debug("_import_path(%r, module_name=%r)", path, module_name)

    if not isfile(path):
        raise ResourceNotFoundError("Module path %r does not exist" % path)

    elif ExtensionFileLoader is not None:
        loader = ExtensionFileLoader(module_name, path)
        return loader.load_module(module_name)

    elif imp is not None:  # pragma: no cover
        return imp.load_dynamic(module_name, path)

    else:  # pragma: no cover
        raise NotImplementedError(
            "Neither `imp` or `ExtensionFileLoader` were imported")


def _read(*paths):
    """
    Iterates over ``files`` and produces string which combines all inputs
    into a single string.

    :raises ResourceNotFoundError:
        Raised if one of the files in ``files`` is missing.
    """
    logger.debug("_read(%r)", paths)

    output = ""
    for path in paths:
        try:
            with open(path, "r") as file_:
                output += file_.read()
        except (OSError, IOError, WindowsError) as error:
            if error.errno == ENOENT:
                raise ResourceNotFoundError("Failed to locate %s" % path)
            raise  # pragma: no cover

    return output


def _ffi(
        module_name=MODULE_NAME, headers=HEADER_FILES, sources=SOURCE_FILES,
        libraries=LIBRARIES):
    """
    Returns an instance of :class:`FFI` without compiling
    the module.  This function is used internally but also
    as an entrypoint in the setup.py for `cffi_modules`.

    :keyword str module_name:
        Optional module name to use when setting the source.

    :keyword tuple headers:
        Optional path(s) to the header files.

    :keyword tuple sources:
        Optional path(s) to the source files.
    """
    logger.debug(
        "_ffi(module_name=%r, headers=%r, sources=%r)",
        module_name, headers, sources)

    header = _read(*headers)
    source = _read(*sources)

    ffi = FFI()
    ffi.set_unicode(True)
    ffi.set_source(module_name, source, libraries=libraries)

    # Windows uses SAL annotations which can provide some helpful information
    # about the inputs and outputs to a function.  Rather than require these
    # to be stripped out manually we should strip them out programmatically.
    ffi.cdef(REGEX_SAL_ANNOTATION.sub(" ", header))

    return ffi


def _compile(ffi, tmpdir=None, module_name=MODULE_NAME):
    """
    Performs the compile step, loads the resulting module and then
    return it.

    :param cffi.FFI ffi:
        An instance of :class:`FFI` which you wish to compile and load
        the resulting module for.

    :keyword str tmpdir:
        The path to compile the module to.  By default this will be
        constructed using ``tempfile.mkdtemp(prefix="pywincffi-")``.

    :keyword str module_name:
        Optional name of the module to be imported.

    :returns:
        Returns the module built by compiling the ``ffi`` object.
    """
    if tmpdir is None:
        tmpdir = tempfile.mkdtemp(prefix="pywincffi-")

    logger.debug(
        "_compile(%r, tmpdir=%r, module_name=%r)", ffi, tmpdir, module_name)
    pyd_path = ffi.compile(tmpdir=tmpdir)
    module = _import_path(pyd_path, module_name=module_name)

    # Try to cleanup the temp directory that was created
    # for compiling the module.  In most cases this will
    # remove everything but the built .pyd file.
    shutil.rmtree(tmpdir, ignore_errors=True)

    return module


def load():
    """
    The main function used by pywincffi to load an instance of
    :class:`FFI` and the underlying library.
    """
    try:
        return Loader.get()
    except InternalError:
        try:
            import _pywincffi as pywincffi
        except ImportError:
            pywincffi = _compile(_ffi())

        Loader.set(pywincffi.ffi, LibraryWrapper(pywincffi.lib))

    return Loader.get()
