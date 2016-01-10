import os
import tempfile
from os.path import isdir, isfile

from astroid import scoped_nodes
from mock import Mock

from pywincffi.dev.lint import (
    HEADERS_DIR, SOURCES_DIR, CONSTANTS_HEADER, FUNCTIONS_HEADER, SOURCE_MAIN,
    REGEX_CONSTANT, REGEX_FUNCTION, transform,
    functions_in_file, constants_in_file)
from pywincffi.dev.testutil import TestCase


class TestConstants(TestCase):
    """
    Tests for constants of :mod:`pywincffi.dev.lint`
    """
    def test_headers_dir(self):
        self.assertTrue(isdir(HEADERS_DIR))

    def test_sources_dir(self):
        self.assertTrue(isdir(SOURCES_DIR))

    def test_constants_header(self):
        self.assertTrue(isfile(CONSTANTS_HEADER))

    def test_functions_header(self):
        self.assertTrue(isfile(FUNCTIONS_HEADER))

    def test_source_main(self):
        self.assertTrue(isfile(SOURCE_MAIN))

    def test_regex_function(self):
        self.assertTrue(REGEX_FUNCTION.match("HANDLE Foobar(int foo);"))

    def test_regex_constant(self):
        self.assertTrue(REGEX_CONSTANT.match("#define FOO ..."))


class TestTransform(TestCase):
    """
    Tests for :func:`pywincffi.dev.lint.transform`
    """
    def test_constants_type(self):
        with self.assertRaises(AssertionError):
            transform(Mock(locals={}), constants=None, functions=set())

    def test_functions_type(self):
        with self.assertRaises(AssertionError):
            transform(Mock(locals={}), constants=set(), functions=None)

    def test_registers_constants(self):
        locals_ = {}
        transform(
            Mock(locals=locals_),
            constants=set(["a", "b"]), functions=set())

        for value in ("a", "b"):
            self.assertIn(value, locals_)
            self.assertEqual(len(locals_[value]), 1)
            self.assertIsInstance(locals_[value][0], scoped_nodes.ClassDef)
            self.assertEqual(locals_[value][0].name, value)

    def test_registers_functions(self):
        locals_ = {}
        transform(
            Mock(locals=locals_),
            constants=set(), functions=set(["c", "d"]))

        for value in ("c", "d"):
            self.assertIn(value, locals_)
            self.assertEqual(len(locals_[value]), 1)
            self.assertIsInstance(locals_[value][0], scoped_nodes.FunctionDef)
            self.assertEqual(locals_[value][0].name, value)


class TestFileFunctions(TestCase):
    """
    Tests for :func:`pywincffi.dev.lint.constants_in_file` and
    :func:`pywincffi.dev.lint.functions_in_file`
    """
    def test_functions_in_file(self):
        fd, path = tempfile.mkstemp()
        self.addCleanup(os.remove, path)

        with os.fdopen(fd, "w") as file_:
            print("HANDLE Foo(int foo);", file=file_)
            print("HANDLE Bar(int foo);", file=file_)

        self.assertEqual(functions_in_file(path), set(["Foo", "Bar"]))

    def test_constants_in_file(self):
        fd, path = tempfile.mkstemp()
        self.addCleanup(os.remove, path)

        with os.fdopen(fd, "w") as file_:
            print("#define FOO ...", file=file_)
            print("#define BAR ...", file=file_)

        self.assertEqual(constants_in_file(path), set(["FOO", "BAR"]))
