from os.path import isfile, dirname, basename

from pywincffi.core.testutil import TestCase
from pywincffi.core.dist import Distribution, get_filepath
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
