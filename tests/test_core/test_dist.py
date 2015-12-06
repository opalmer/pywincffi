from os.path import isfile, dirname, basename

try:
    from importlib.machinery import ExtensionFileLoader

    def import_module(module_name, path):
        loader = ExtensionFileLoader(module_name, path)
        return loader.load_module()

except ImportError:
    import imp

    def import_module(module_name, path):
        return imp.load_dynamic(module_name, path)

from cffi import FFI

from pywincffi.core.testutil import TestCase
from pywincffi.core.dist import Distribution, InlineModule, get_filepath
from pywincffi.exceptions import ResourceNotFoundError


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
    def test_sets_unicode(self):
        ffi, _ = Distribution.inline()
        self.assertTrue(ffi._windows_unicode)

    def test_ffi_type(self):
        ffi, _ = Distribution.inline()
        self.assertIsInstance(ffi, FFI)

    def test_caches_inline_module(self):
        Distribution.inline()
        self.assertIsInstance(Distribution._pywincffi, InlineModule)

    def test_calling_inline_resets_cache(self):
        Distribution.inline()
        module = Distribution._pywincffi
        Distribution.inline()
        self.assertIsNot(Distribution._pywincffi, module)

    def test_inline_produces_function(self):
        ffi, library = Distribution.inline()
        func = getattr(library, self.function_name)
        self.assertEqual(func(1), 2)


class TestDistributionOutOfLine(TestDistributionLoadBaseTest):
    """
    Tests for :meth:`pywincffi.core.dist.Distribution.out_of_line`
    """
    def test_sets_unicode(self):
        tmpdir = self.tempdir()
        ffi, _ = Distribution.out_of_line(tmpdir=tmpdir)
        self.assertTrue(ffi._windows_unicode)

    def test_ffi_type(self):
        ffi, _ = Distribution.out_of_line()
        self.assertIsInstance(ffi, FFI)

    def test_library_path(self):
        tmpdir = self.tempdir()
        _, path = Distribution.out_of_line(tmpdir=tmpdir)
        self.assertTrue(isfile(path))

    def test_can_import_compiled_module(self):
        tmpdir = self.tempdir()
        _, path = Distribution.out_of_line(tmpdir=tmpdir)
        import_module(Distribution.MODULE_NAME, path)

    def test_compiled_module_has_ffi_instance(self):
        tmpdir = self.tempdir()
        _, path = Distribution.out_of_line(tmpdir=tmpdir)
        module = import_module(Distribution.MODULE_NAME, path)
        self.assertTrue(hasattr(module, "ffi"))
        self.assertEqual(
            module.ffi.__class__.__name__, "CompiledFFI")

    def test_compiled_module_has_library_instance(self):
        tmpdir = self.tempdir()
        _, path = Distribution.out_of_line(tmpdir=tmpdir)
        module = import_module(Distribution.MODULE_NAME, path)
        self.assertTrue(hasattr(module, "lib"))
        self.assertEqual(type(module.lib).__name__, "CompiledLib")

    def test_compiled_module_produces_function(self):
        tmpdir = self.tempdir()
        _, path = Distribution.out_of_line(tmpdir=tmpdir)
        module = import_module(Distribution.MODULE_NAME, path)
        func = getattr(module.lib, self.function_name)
        self.assertEqual(func(1), 2)
