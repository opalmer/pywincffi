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
import warnings
from errno import ENOENT
from os.path import join, isfile
from pkg_resources import resource_filename

from cffi import FFI

from pywincffi.core.logger import get_logger
from pywincffi.exceptions import ResourceNotFoundError

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
        "pywincffi", join("core", "cdefs", "headers", "constants.h")),
    resource_filename(
        "pywincffi", join("core", "cdefs", "headers", "structs.h")),
    resource_filename(
        "pywincffi", join("core", "cdefs", "headers", "functions.h")))
SOURCE_FILES = (
    resource_filename(
        "pywincffi", join("core", "cdefs", "sources", "main.c")), )
LIBRARIES = ("kernel32", "user32")
REGEX_SAL_ANNOTATION = re.compile(
    r"\b(_In_|_Inout_|_Out_|_Outptr_|_Reserved_)(opt_)?\b")


class Module(object):  # pylint: disable=too-few-public-methods
    """
    Used and returned by :func:`load`.  This class stores information
    about a loaded module and is
    """
    cache = None

    def __init__(self, module, mode):
        if self.cache is not None:
            warnings.warn(
                "Module() was instanced multiple times", RuntimeWarning)

        self.module = module
        self.mode = mode
        self.ffi = module.ffi
        self.lib = module.lib

    def __repr__(self):
        return "%r (%s)" % (self.module, self.mode)

    def __iter__(self):
        """
        Override the original __iter__ so tuple unpacking can be
        used to pull out ffi and lib.  This will allow
        """
        yield self.ffi
        yield self.lib


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
    :class:`FFI` and the underlying build library.
    """
    if Module.cache is not None:
        return Module.cache

    logger.debug("load()")
    try:
        import _pywincffi
        Module.cache = Module(_pywincffi, "prebuilt")

    except ImportError:
        Module.cache = Module(_compile(_ffi()), "compiled")

    return Module.cache
