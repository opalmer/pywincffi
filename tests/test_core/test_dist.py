import imp
import os
import sys
import types
from os.path import isfile, dirname, basename, join

from cffi import FFI
from mock import patch

from pywincffi.core.config import config
from pywincffi.core.dist import (
    __all__, Distribution, InlineModule, get_filepath, ffi, load)
from pywincffi.core.testutil import TestCase
from pywincffi.exceptions import ResourceNotFoundError


try:
    # pylint: disable=wrong-import-order
    from importlib.machinery import ExtensionFileLoader

    def import_module(module_name, path):
        loader = ExtensionFileLoader(module_name, path)
        return loader.load_module(module_name)

    def new_module(name):
        return types.ModuleType(name)

except ImportError:
    def import_module(module_name, path):
        return imp.load_dynamic(module_name, path)

    def new_module(name):
        return imp.new_module(name)


class TestGetFilepath(TestCase):
    """
    Tests for ``pywincffi.core.get_filepath``
    """
    def test_headers(self):
        for path in Distribution.HEADERS:
            root = dirname(path)
            filename = basename(path)
            self.assertTrue(isfile(get_filepath(root, filename)))

    def test_sources(self):
        for path in Distribution.SOURCES:
            root = dirname(path)
            filename = basename(path)
            self.assertTrue(isfile(get_filepath(root, filename)))

    def test_file_does_not_exist(self):
        with self.assertRaises(ResourceNotFoundError):
            get_filepath("", "")


class TestDistributionHeaders(TestCase):
    """
    Tests for ``pywincffi.core.dist.Distribution.HEADERS``
    """
    def test_variable_type(self):
        self.assertIsInstance(Distribution.HEADERS, tuple)

    def test_value_types(self):
        for value in Distribution.HEADERS:
            self.assertIsInstance(value, str)

    def test_is_file(self):
        for value in Distribution.HEADERS:
            self.assertTrue(isfile(value))


class TestDistributionSources(TestCase):
    """
    Tests for ``pywincffi.core.dist.Distribution.SOURCES``
    """
    def test_variable_type(self):
        self.assertIsInstance(Distribution.SOURCES, tuple)

    def test_value_types(self):
        for value in Distribution.SOURCES:
            self.assertIsInstance(value, str)

    def test_is_file(self):
        for value in Distribution.SOURCES:
            self.assertTrue(isfile(value))


class TestDistributionLoadDefinitions(TestCase):
    def test_header(self):
        expected = ""
        for path in Distribution.HEADERS:
            with open(path, "r") as file_:
                expected += file_.read()

        self.assertEqual(expected, Distribution.load_definitions()[0])

    def test_source(self):
        expected = ""
        for path in Distribution.SOURCES:
            with open(path, "r") as file_:
                expected += file_.read()

        self.assertEqual(expected, Distribution.load_definitions()[1])


class TestDistributionLoadBaseTest(TestCase):
    HEADERS = None
    SOURCES = None
    count = 0

    def setUp(self):
        super(TestDistributionLoadBaseTest, self).setUp()
        # Capture the existing values
        self._pywincffi = Distribution._pywincffi
        self._headers = Distribution.HEADERS
        self._sources = Distribution.SOURCES
        self.count += 1
        self.function_name = "add%s" % self.count
        self._pywincffi_module = sys.modules.pop(
            Distribution.MODULE_NAME, None)

        headers = self.HEADERS
        if self.HEADERS is None:
            headers = self.generate_headers()

        sources = self.SOURCES
        if self.SOURCES is None:
            sources = self.generate_sources()

        # Reset the to something we can test with
        Distribution._pywincffi = None
        Distribution.HEADERS = headers
        Distribution.SOURCES = sources

    def tearDown(self):
        super(TestDistributionLoadBaseTest, self).tearDown()
        Distribution._pywincffi = self._pywincffi
        Distribution.HEADERS = self._headers
        Distribution.SOURCES = self._sources

        if self._pywincffi_module is not None:
            sys.modules.update(_pywincffi=self._pywincffi_module)

    def generate_headers(self):
        path = self.tempfile("int %s(int);" % self.function_name)
        return path,

    def generate_sources(self):
        path = self.tempfile(
            "int %s(int value) {return value + 1;}" % self.function_name)
        return path,


class TestDistributionInline(TestDistributionLoadBaseTest):
    """
    Tests for :meth:`pywincffi.core.dist.Distribution.inline`
    """
    def configure(self, config_):
        super(TestDistributionInline, self).configure(config_)
        config.set("pywincffi", "library", "inline")

    def test_sets_unicode(self):
        ffi_, _ = Distribution.inline()
        with self.assertRaises(ValueError):
            ffi_.set_unicode(True)

    def test_ffi_type(self):
        ffi_, _ = Distribution.inline()
        self.assertIsInstance(ffi_, FFI)

    def test_caches_inline_module(self):
        Distribution.inline()
        self.assertIsInstance(Distribution._pywincffi, InlineModule)

    def test_calling_inline_resets_cache(self):
        Distribution.inline()
        module = Distribution._pywincffi
        Distribution.inline()
        self.assertIsNot(Distribution._pywincffi, module)

    def test_inline_produces_function(self):
        _, library = Distribution.inline()
        func = getattr(library, self.function_name)
        self.assertEqual(func(1), 2)


class TestDistributionOutOfLine(TestDistributionLoadBaseTest):
    """
    Tests for :meth:`pywincffi.core.dist.Distribution.out_of_line`
    """
    def configure(self, config_):
        super(TestDistributionOutOfLine, self).configure(config_)
        config.set("pywincffi", "library", "precompiled")

    def test_sets_unicode(self):
        ffi_, _ = Distribution.out_of_line()

        with self.assertRaises(ValueError):
            ffi_.set_unicode(True)

    def test_ffi_type(self):
        ffi_, _ = Distribution.out_of_line()
        self.assertIsInstance(ffi_, FFI)

    def test_library_path(self):
        _, path = Distribution.out_of_line()
        self.assertTrue(isfile(path))

    def test_can_import_compiled_module(self):
        _, path = Distribution.out_of_line()
        import_module(Distribution.MODULE_NAME, path)

    def test_compiled_module_has_ffi_instance(self):
        _, path = Distribution.out_of_line()
        module = import_module(Distribution.MODULE_NAME, path)
        self.assertTrue(hasattr(module, "ffi"))
        self.assertEqual(
            module.ffi.__class__.__name__, "CompiledFFI")

    def test_compiled_module_has_library_instance(self):
        _, path = Distribution.out_of_line()
        module = import_module(Distribution.MODULE_NAME, path)
        self.assertTrue(hasattr(module, "lib"))
        self.assertEqual(type(module.lib).__name__, "CompiledLib")

    def test_compiled_module_produces_function(self):
        _, path = Distribution.out_of_line()
        module = import_module(Distribution.MODULE_NAME, path)
        func = getattr(module.lib, self.function_name)
        self.assertEqual(func(1), 2)


class TestDistributionLoad(TestDistributionLoadBaseTest):
    def test_imports_module_cache(self):
        config.set("pywincffi", "library", "precompiled")
        module = new_module(Distribution.MODULE_NAME)
        module.ffi = 3
        module.lib = 4
        sys.modules.update({Distribution.MODULE_NAME: module})
        self.addCleanup(sys.modules.pop, Distribution.MODULE_NAME)
        self.assertEqual(Distribution.load(), (3, 4))
        self.assertIs(Distribution._pywincffi, module)

    def test_compiles_module_inline(self):
        config.set("pywincffi", "library", "inline")

        with patch.object(Distribution, "_pywincffi", None):
            ffi_, library = Distribution.load()

        self.assertIsInstance(ffi_, FFI)
        self.assertEqual(library.__class__.__name__, "FFILibrary")

    def test_calls_inline_for_compile_error(self):
        tempdir = self.tempdir()
        with open(join(tempdir, "__init__.py"), "w"):
            pass

        with open(join(tempdir, "_pywincffi.py"), "w") as _pywincffi:
            _pywincffi.write("raise ImportError('fail')" + os.linesep)

        sys.path.insert(0, tempdir)
        self.addCleanup(sys.path.remove, tempdir)

        _, lib = Distribution.load()
        self.assertIsInstance(Distribution._pywincffi, InlineModule)
        func = getattr(lib, self.function_name)
        self.assertEqual(func(1), 2)


class TestFFIFunction(TestDistributionLoadBaseTest):
    def test_all_export(self):
        self.assertIn("ffi", __all__)

    def test_calls_implementation_function(self):
        with patch.object(Distribution, "out_of_line") as mocked:
            ffi()

        mocked.assert_called_with(compile_=False)

    def test_return_value(self):
        with patch.object(Distribution, "out_of_line", return_value=(1, 2)):
            result = ffi()

        self.assertEqual(result, 1)


class TestLoadFunction(TestDistributionLoadBaseTest):
    def test_all_export(self):
        self.assertIn("load", __all__)

    def test_calls_implementation_function(self):
        with patch.object(Distribution, "load") as mocked:
            load()

        mocked.assert_called_once_with()

    def test_return_value(self):
        with patch.object(Distribution, "load", return_value=(1, 2)):
            result = load()

        self.assertEqual(result, (1, 2))
