from __future__ import print_function

import binascii
import os
import shutil
import sys
import tempfile
import warnings
from os.path import isfile, dirname

from cffi import FFI
from mock import Mock, patch

from pywincffi.core.dist import (
    MODULE_NAME, HEADER_FILES, SOURCE_FILES, Module, _import_path, _ffi,
    _compile, _read, load)
from pywincffi.core.testutil import TestCase
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
    def setUp(self):
        super(TestModule, self).setUp()
        Module.cache = None

    def tearDown(self):
        super(TestModule, self).tearDown()
        Module.cache = None
        sys.modules.pop("_pywincffi", None)

    def test_cache_default(self):
        self.assertIsNone(Module.cache)

    def test_double_cache_produces_warning(self):
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
        self.module_name = \
            "m" + binascii.b2a_hex(os.urandom(6)).decode("utf-8")
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
    def test_sets_unicode(self):
        with patch.object(FFI, "set_unicode") as mocked_set_unicode:
            _ffi()

        mocked_set_unicode.assert_called_once_with(True)

    def test_set_source(self):
        with patch.object(FFI, "set_source") as mocked_set_source:
            _ffi()

        mocked_set_source.assert_called_once_with(
            MODULE_NAME, _read(*SOURCE_FILES))

    def test_cdef(self):
        with patch.object(FFI, "cdef") as mocked_cdef:
            _ffi()

        mocked_cdef.assert_called_with(_read(*HEADER_FILES))


class TestCompile(TestCase):
    """Tests for :func:`pywincffi.core.dist._compile`"""
    def setUp(self):
        super(TestCompile, self).setUp()
        self.header_files = HEADER_FILES[:]
        self.source_files = SOURCE_FILES[:]

    def tearDown(self):
        super(TestCompile, self).tearDown()
        HEADER_FILES[:] = self.header_files
        SOURCE_FILES[:] = self.source_files
        Module.cache = None
        sys.modules.pop("_pywincffi", None)

    def test_compile(self):
        # Create fake header
        fd, path = tempfile.mkstemp()
        self.addCleanup(os.remove, path)
        HEADER_FILES[:] = [path]

        with os.fdopen(fd, "w") as header:
            header.write("int add(int, int);")

        # Create fake source
        fd, path = tempfile.mkstemp()
        self.addCleanup(os.remove, path)
        SOURCE_FILES[:] = [path]
        with os.fdopen(fd, "w") as source:
            source.write("int add(int a, int b) {return a + b;}")

        ffi = _ffi()
        module = _compile(ffi)
        self.assertEqual(module.lib.add(1, 2), 3)

    def test_compile_uses_provided_tempdir(self):
        # Create fake header
        fd, path = tempfile.mkstemp()
        self.addCleanup(os.remove, path)
        HEADER_FILES[:] = [path]

        with os.fdopen(fd, "w") as header:
            header.write("int add(int, int);")

        # Create fake source
        fd, path = tempfile.mkstemp()
        self.addCleanup(os.remove, path)
        SOURCE_FILES[:] = [path]
        with os.fdopen(fd, "w") as source:
            source.write("int add(int a, int b) {return a + b;}")

        tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmpdir, ignore_errors=True)

        ffi = _ffi()
        module = _compile(ffi, tmpdir=tmpdir)
        self.assertEqual(dirname(module.__file__), tmpdir)


class TestLoad(TestCase):
    """Tests for :func:`pywincffi.core.dist.load`"""
    def tearDown(self):
        super(TestLoad, self).tearDown()
        Module.cache = None
        sys.modules.pop("_pywincffi", None)

    def test_cache(self):
        cached = object()
        Module.cache = cached
        self.assertIs(load(), cached)

    def test_prebuilt(self):
        fake_module = Mock(ffi=1, lib=2)
        sys.modules["_pywincffi"] = fake_module
        loaded = load()
        self.assertEqual(loaded.mode, "prebuilt")

    def test_compiled(self):
        # Setting _pywincffi to None in sys.modules will force
        # 'import _pywincffi' to fail forcing load() to
        # compile the module.
        sys.modules["_pywincffi"] = None
        loaded = load()
        self.assertEqual(loaded.mode, "compiled")
