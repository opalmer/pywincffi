from pywincffi.core import dist
from pywincffi.dev.testutil import (
    TestCase, skip_unless_python2, skip_unless_python3)
from pywincffi.util import string_to_cdata


class TestStringToCData(TestCase):
    """
    Tests for :func:`pywincffi.util.string_to_cdata`
    """
    def assert_type(self, cdata, expected_cname):
        ffi, _ = dist.load()
        typeof = ffi.typeof(cdata)
        self.assertEqual(type(cdata).__name__, "CDataOwn")
        self.assertEqual(typeof.kind, "array")
        self.assertEqual(typeof.cname, expected_cname)

    def assert_value(self, cdata, expected_value):
        ffi, _ = dist.load()
        self.assertEqual(ffi.string(cdata), expected_value)
    #
    # Python 2 tests
    #

    @skip_unless_python2
    def test_py2_string_forced_to_unicode(self):
        value = self.random_string(6)
        cdata = string_to_cdata(str(value))
        self.assert_type(cdata, "wchar_t[]")
        self.assert_value(cdata, value)

    @skip_unless_python2
    def test_py2_string_explicit_conversion_to_string(self):
        value = self.random_string(6)
        cdata = string_to_cdata(str(value), unicode_cast=False)
        self.assert_type(cdata, "char[]")
        self.assert_value(cdata, value)

    @skip_unless_python2
    def test_py2_unicode(self):
        value = self.random_string(6)

        # pylint: disable=undefined-variable
        cdata = string_to_cdata(unicode(value))
        self.assert_type(cdata, "wchar_t[]")
        self.assert_value(cdata, value)

    @skip_unless_python2
    def test_py2_other(self):
        with self.assertRaises(TypeError):
            string_to_cdata(1)

    #
    # Python 3 tests
    #

    @skip_unless_python3
    def test_py3_string(self):
        value = self.random_string(6)
        cdata = string_to_cdata(value)
        self.assert_type(cdata, "wchar_t[]")
        self.assert_value(cdata, value)

    @skip_unless_python3
    def test_py3_unicode_cast_disabled_has_no_effect(self):
        value = self.random_string(6)
        cdata = string_to_cdata(value, unicode_cast=False)
        self.assert_type(cdata, "wchar_t[]")
        self.assert_value(cdata, value)

    @skip_unless_python3
    def test_py3_bytes(self):
        # Bytes will probably be one type that's
        # commonly passed in.  Since we shouldn't
        # make assumptions about encoding we should
        # raise a TypeError.
        with self.assertRaises(TypeError):
            string_to_cdata(bytes("", "utf-8"))

    @skip_unless_python3
    def test_py3_other(self):
        with self.assertRaises(TypeError):
            string_to_cdata(1)
