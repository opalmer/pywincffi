from __future__ import print_function

import os
import shutil
import sys
import tempfile
from os.path import isfile, dirname

from cffi import FFI
from mock import patch

from pywincffi.core import dist
from pywincffi.core.dist import (
    MODULE_NAME, HEADER_FILES, SOURCE_FILES, LIBRARIES, LibraryWrapper, Loader,
    _import_path, _ffi, _compile, _read, load)
from pywincffi.dev.testutil import TestCase
from pywincffi.exceptions import ResourceNotFoundError, InternalError


class TestDistConstants(TestCase):
    def test_module_name(self):
        self.assertEqual(MODULE_NAME, "_pywincffi")

    def test_header_files_exist(self):
        for path in HEADER_FILES:
            self.assertTrue(isfile(path))

    def test_source_files_exist(self):
        for path in SOURCE_FILES:
            self.assertTrue(isfile(path))


class TestLibraryWrapper(TestCase):
    """
    Tests for :class:`pywincffi.core.dist.LibraryWrapper`
    """
    def setUp(self):
        super(TestLibraryWrapper, self).setUp()
        _, library = load()
        self.library = library._library
        self.wrapper = LibraryWrapper(self.library)

    def test_meta_dir(self):
        self.assertEqual(
            set(dir(self.wrapper)),
            set(dir(self.library) +
                list(self.wrapper._RUNTIME_CONSTANTS.keys()))
        )

    def test_meta_dict(self):
        library_dict = self.library.__dict__.copy()
        library_dict.update(self.wrapper._RUNTIME_CONSTANTS)
        self.assertEqual(self.wrapper.__dict__, library_dict)

    def test_meta_getattr_on_library(self):
        for attribute in dir(self.wrapper):
            if attribute in self.wrapper._RUNTIME_CONSTANTS:
                continue

            self.assertEqual(
                getattr(self.wrapper, attribute),
                getattr(self.library, attribute))

    def test_meta_getattr_on_wrapper(self):
        for attribute in self.wrapper._RUNTIME_CONSTANTS:
            self.assertEqual(
                getattr(self.wrapper, attribute),
                self.wrapper._RUNTIME_CONSTANTS[attribute])

    def test_meta_getattr_failure(self):
        with self.assertRaises(AttributeError):
            self.wrapper.FOOBAR  # pylint: disable=pointless-statement


class TestLoader(TestCase):
    """
    Tests for :class:`pywincffi.core.dist.Loader`
    """
    def setUp(self):
        super(TestLoader, self).setUp()
        mock = patch.object(Loader, "cache", None)
        mock.start()
        self.addCleanup(mock.stop)

    def test_set(self):
        a, b = self.random_string(6), self.random_string(6)
        Loader.set(a, b)
        self.assertEqual(Loader.cache, (a, b))

    def test_set_works_once(self):
        a, b = self.random_string(6), self.random_string(6)
        c, d = self.random_string(6), self.random_string(6)
        Loader.set(a, b)

        with self.assertRaises(InternalError):
            Loader.set(c, d)

        self.assertEqual(Loader.cache, (a, b))

    def test_get(self):
        a, b = self.random_string(6), self.random_string(6)
        Loader.set(a, b)
        self.assertEqual(Loader.get(), (a, b))

    def test_get_fails_if_called_before_set(self):
        with self.assertRaises(InternalError):
            Loader.get()


class TestImportPath(TestCase):
    """Tests for :func:`pywincffi.core.dist._import_path`"""
    def setUp(self):
        super(TestImportPath, self).setUp()
        self.module_name = self.random_string(16)
        self.header = "int add(int, int);"
        self.source = "int add(int a, int b) {return a + b;}"

    def build(self):
        ffi = FFI()
        ffi.set_source(self.module_name, self.source)
        ffi.cdef(self.header)
        tmpdir = tempfile.mkdtemp(prefix="pywincffi-tests-")
        self.addCleanup(shutil.rmtree, tmpdir, ignore_errors=True)
        return self.module_name, ffi.compile(tmpdir=tmpdir)

    def test_invalid_path(self):
        with self.assertRaises(ResourceNotFoundError):
            _import_path("")

    def test_imported_module(self):
        name, path = self.build()
        module = _import_path(path, module_name=name)
        self.assertTrue(hasattr(module, "lib"))
        self.assertTrue(hasattr(module.lib, "add"))
        self.assertEqual(module.lib.add(1, 2), 3)


class TestRead(TestCase):
    """Tests for :func:`pywincffi.core.dist._read`"""
    def test_loads_files(self):
        temp_files = []
        expected_output = ""
        for i in range(10):
            expected_output += str(i)
            fd, path = tempfile.mkstemp()
            self.addCleanup(os.remove, path)
            with os.fdopen(fd, "w") as file_:
                file_.write(str(i))
            temp_files.append(path)

        self.assertEqual(_read(*temp_files), expected_output)

    def test_raises_resource_not_found_error(self):
        fd, path = tempfile.mkstemp()
        os.close(fd)
        os.remove(path)
        with self.assertRaises(ResourceNotFoundError):
            _read(path)


class TestFFI(TestCase):
    """Tests for :func:`pywincffi.core.dist._ffi`"""
    def setUp(self):
        self.module_name = self.random_string(16)
        self.addCleanup(sys.modules.pop, self.module_name, None)

    def test_calls_set_unicode(self):
        # Certain types require set_unicode to be called so
        # this test will fail if ffi.set_unicode(True) is never
        # called in our core library.
        fd, header_path = tempfile.mkstemp(suffix=".h")
        with os.fdopen(fd, "w") as file_:
            file_.write("BOOL Foobar(LPTSTR);")

        _ffi(module_name=self.module_name, sources=[], headers=[header_path])

    def test_default_source_files(self):
        with patch.object(FFI, "set_source") as mocked_set_source:
            _ffi(module_name=self.module_name)

        mocked_set_source.assert_called_once_with(
            self.module_name, _read(*SOURCE_FILES), libraries=LIBRARIES)

    def test_alternate_source_files(self):
        _, path = tempfile.mkstemp(suffix=".h")

        with patch.object(FFI, "set_source") as mocked_set_source:
            _ffi(module_name=self.module_name, sources=[path])

        mocked_set_source.assert_called_once_with(
            self.module_name, _read(*[path]), libraries=LIBRARIES)


class TestCompile(TestCase):
    """Tests for :func:`pywincffi.core.dist._compile`"""
    def setUp(self):
        super(TestCompile, self).setUp()
        self.module_name = self.random_string(16)
        self.addCleanup(sys.modules.pop, self.module_name, None)
        # self.addCleanup(setattr, Module, "cache", None)

    def test_compile(self):
        # Create fake header
        fd, header = tempfile.mkstemp(suffix=".h")
        self.addCleanup(os.remove, header)
        with os.fdopen(fd, "w") as file_:
            file_.write("int add(int, int);")

        # Create fake source
        fd, source = tempfile.mkstemp(suffix=".c")
        self.addCleanup(os.remove, source)
        with os.fdopen(fd, "w") as file_:
            file_.write(
                "int add(int a, int b) {return a + b;}")

        ffi = _ffi(
            module_name=self.module_name, sources=[source], headers=[header])
        module = _compile(ffi, module_name=self.module_name)
        self.assertEqual(module.lib.add(1, 2), 3)

    def test_compile_uses_provided_tempdir(self):
        # Create fake header
        fd, header = tempfile.mkstemp(suffix=".h")
        self.addCleanup(os.remove, header)
        with os.fdopen(fd, "w") as file_:
            file_.write("int add(int, int);")

        # Create fake source
        fd, source = tempfile.mkstemp(suffix=".c")
        self.addCleanup(os.remove, source)
        with os.fdopen(fd, "w") as file_:
            file_.write("int add(int a, int b) {return a + b;}")

        tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmpdir, ignore_errors=True)

        ffi = _ffi(
            module_name=self.module_name, sources=[source], headers=[header])
        module = _compile(ffi, tmpdir=tmpdir, module_name=self.module_name)
        self.assertEqual(dirname(module.__file__), tmpdir)


class TestLoad(TestCase):
    """Tests for :func:`pywincffi.core.dist.load`"""
    def setUp(self):
        super(TestLoad, self).setUp()
        mock = patch.object(Loader, "cache", None)
        mock.start()
        self.addCleanup(sys.modules.pop, MODULE_NAME, None)
        self.addCleanup(mock.stop)

    def test_prebuilt(self):
        class FakeModule(object):
            ffi = None

            class lib(object):
                a, b = self.random_string(6), self.random_string(6)

        sys.modules[MODULE_NAME] = FakeModule
        _, library = load()

        self.assertEqual(library.a, FakeModule.lib.a)
        self.assertEqual(library.b, FakeModule.lib.b)

    def test_compiled(self):
        # Python 3.5 changes the behavior of None in sys.modules. So
        # long as other Python versions pass, skipping this should
        # be ok.
        if sys.version_info[0:2] >= (3, 5):
            self.skipTest("Python 3.5 not suppoted in this test")

        # Setting _pywincffi to None in sys.modules will force
        # 'import _pywincffi' to fail forcing load() to
        # compile the module.
        sys.modules[MODULE_NAME] = None

        with patch.object(dist, "_compile") as mocked:
            load()

        mocked.assert_called_once()
