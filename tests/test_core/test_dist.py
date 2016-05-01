from __future__ import print_function

import os
import shutil
import sys
import tempfile
import warnings
from os.path import isfile, dirname

from cffi import FFI
from mock import Mock, patch

from pywincffi.core.dist import (
    MODULE_NAME, HEADER_FILES, SOURCE_FILES, LIBRARIES, Module, _import_path,
    _ffi, _compile, _read, load)
from pywincffi.dev.testutil import TestCase
from pywincffi.exceptions import ResourceNotFoundError


class TestConstants(TestCase):
    def test_module_name(self):
        self.assertEqual(MODULE_NAME, "_pywincffi")

    def test_header_files_exist(self):
        for path in HEADER_FILES:
            self.assertTrue(isfile(path))

    def test_source_files_exist(self):
        for path in SOURCE_FILES:
            self.assertTrue(isfile(path))


class TestModule(TestCase):
    """
    Tests for :class:`pywincffi.core.dist.Module`
    """
    def test_double_cache_produces_warning(self):
        self.addCleanup(setattr, Module, "cache", None)
        Module.cache = ""

        with warnings.catch_warnings(record=True) as caught:
            Module(Mock(ffi=None, lib=None), None)

        warning = caught.pop(0)
        self.assertIs(warning.category, RuntimeWarning)
        self.assertEqual(
            warning.message.args[0], "Module() was instanced multiple times")

    def test_attributes(self):
        m = Module(Mock(ffi=1, lib=2), "foo")
        self.assertEqual(m.ffi, 1)
        self.assertEqual(m.lib, 2)
        self.assertEqual(m.mode, "foo")

    def test_tuple_unpacking(self):
        m = Module(Mock(ffi=1, lib=2), "foo")
        unpacked = tuple(m)
        self.assertEqual(len(unpacked), 2)
        self.assertEqual(unpacked[0], 1)
        self.assertEqual(unpacked[1], 2)


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

    def test_default_cdefs(self):
        with patch.object(FFI, "cdef") as mocked_cdef:
            _ffi(module_name=self.module_name)

        mocked_cdef.assert_called_with(_read(*HEADER_FILES))

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
        self.addCleanup(setattr, Module, "cache", None)

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
        self.addCleanup(setattr, Module, "cache", None)
        Module.cache = None

        if MODULE_NAME in sys.modules:
            self.addCleanup(
                sys.modules.__setitem__, MODULE_NAME, sys.modules[MODULE_NAME])
            sys.modules.pop(MODULE_NAME)

    def test_cache(self):
        cached = object()
        Module.cache = cached
        self.assertIs(load(), cached)

    def test_prebuilt(self):
        fake_module = Mock(ffi=1, lib=2)
        sys.modules[MODULE_NAME] = fake_module
        loaded = load()
        self.assertEqual(loaded.mode, "prebuilt")

    def test_compiled(self):
        # Setting _pywincffi to None in sys.modules will force
        # 'import _pywincffi' to fail forcing load() to
        # compile the module.
        sys.modules[MODULE_NAME] = None
        loaded = load()
        self.assertEqual(loaded.mode, "compiled")
