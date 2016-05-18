import cffi

from pywincffi.core import typesbase
from pywincffi.dev.testutil import TestCase


class TestCFFICDataWrapper(TestCase):
    """
    Tests for :class:`pywincffi.core.typesbase.CFFICDataWrapper`
    """
    def test_instantiate(self):
        o = typesbase.CFFICDataWrapper("char *")
        self.assertIsNotNone(o)

    def test_simple_struct_set_and_get(self):
        o = typesbase.CFFICDataWrapper("""
            struct _point {
                float x;
                float y;
                float z;
            } *
        """)
        o.x = 123.0
        o.y = 456.0
        o.z = 789.0
        self.assertAlmostEqual(o.x, 123.0, places=2)
        self.assertAlmostEqual(o.y, 456.0, places=2)
        self.assertAlmostEqual(o.z, 789.0, places=2)

    def test_char_array_set_and_get(self):
        o = typesbase.CFFICDataWrapper("char [256]")
        content = b"abcdefghijklmnopqrstuvwxyz"
        content_len = len(content)
        for i in range(256):
            # Have Python 3 return a len()==1 bytes object
            start = i % content_len
            finish = start + 1
            o[i] = content[start:finish]
        for i in range(256):
            self.assertEqual(o[i], content[i % content_len])

    def test_char_array_set_and_ffi_string(self):
        ffi = cffi.FFI()
        o = typesbase.CFFICDataWrapper("char [256]")
        content = b"0123456789"
        content_len = len(content)
        for i in range(content_len):
            # Have Python 3 return a len()==1 bytes object
            o[i] = content[i:i+1]
        # must use wrapped cdata to apply ffi.string in this case
        # won't be needed for struct members as other tests verify
        self.assertEqual(ffi.string(o._cdata), content)

    def test_simple_struct_array_set_and_get(self):
        o = typesbase.CFFICDataWrapper("""
            struct _time {
                int hour;
                int minute;
                int second;
            } [20]
        """)
        for i in range(20):
            o[i].hour = i
            o[i].minute = (12 - i*2) % 60
            o[i].second = (i * 9871) % 60
        for i in range(20):
            self.assertEqual(o[i].hour, i)
            self.assertEqual(o[i].minute, (12 - i*2) % 60)
            self.assertEqual(o[i].second, (i * 9871) % 60)

    def test_complex_struct_set_and_get(self):
        ffi = cffi.FFI()
        o = typesbase.CFFICDataWrapper("""
            struct _complex {
                char uuid[36];
                unsigned int fd;
                unsigned int type;
                union _u {
                    struct _file {
                        unsigned int inode;
                        char name[256];
                    } file;
                    struct _tcp_socket {
                        char bind_addr[4];
                        unsigned short int port;
                    } socket;
                } u;
            } *
        """)
        _uuid = b"01234567-abcd-abcd-abcd-0123456789ab"
        o.uuid = _uuid
        o.fd = 0xfd
        o.type = 2
        o.u.file.inode = 12345
        _file_name = b"the-filename.test"
        o.u.file.name = _file_name
        self.assertEqual(ffi.unpack(o.uuid, len(_uuid)), _uuid)
        self.assertEqual(o.fd, 0xfd)
        self.assertEqual(o.type, 2)
        self.assertEqual(o.u.file.inode, 12345)
        self.assertEqual(
            ffi.unpack(o.u.file.name, len(_file_name)),
            _file_name
        )

    def test_externally_provided_ffi(self):
        ffi = cffi.FFI()
        ffi.cdef("""
            typedef struct _person {
                wchar_t first_name[32];
                wchar_t last_name[32];
            } person_t;
        """)
        o = typesbase.CFFICDataWrapper("person_t *", ffi)
        o.first_name = u"First Name"
        o.last_name = u"Last Name"
        self.assertEqual(ffi.string(o.first_name), u"First Name")
        self.assertEqual(ffi.string(o.last_name), u"Last Name")


_ffi_with_circle_t = cffi.FFI()
_ffi_with_circle_t.cdef("""
    typedef struct _circle {
        float x;
        float y;
        float radius;
    } circle_t;
""")


class _Circle(typesbase.CFFICDataWrapper):
    """
    Used in TestDerivedStructTypes.
    """
    def __init__(self):
        super(_Circle, self).__init__("circle_t *", _ffi_with_circle_t)


class _CircleWithArgs(_Circle):
    """
    Used in TestDerivedStructTypes.
    """
    def __init__(self, x=1.23, y=4.56, radius=7.89):
        super(_CircleWithArgs, self).__init__()
        self.x = x
        self.y = y
        self.radius = radius


class _CircleWithProperties(_CircleWithArgs):
    """
    Used in TestDerivedStructTypes.
    """
    @property
    def radius(self):
        return self._cdata.radius

    @radius.setter
    def radius(self, value):
        if not isinstance(value, float):
            raise TypeError("%r not a float" % value)
        if value < 0.0:
            raise ValueError("negative radius")
        self._cdata.radius = value


class TestDerivedStructTypes(TestCase):
    """
    Tests for types based on :class:`pywincffi.core.typesbase.CFFICDataWrapper`
    """

    def test_derived_circle_simple(self):
        c = _Circle()
        c.x = 0.0  # pylint: disable=attribute-defined-outside-init
        c.y = 0.0  # pylint: disable=attribute-defined-outside-init
        c.radius = 1.0  # pylint: disable=attribute-defined-outside-init
        self.assertAlmostEqual(c.x, 0.0, places=2)
        self.assertAlmostEqual(c.y, 0.0, places=2)
        self.assertAlmostEqual(c.radius, 1.0, places=2)

    def test_derived_circle_bad_attr(self):
        c = _Circle()
        with self.assertRaises(AttributeError):
            # pylint: disable=attribute-defined-outside-init
            c.no_such_attr = 42

    def test_derived_circle_with_args(self):
        c = _CircleWithArgs()
        self.assertAlmostEqual(c.x, 1.23, places=2)
        self.assertAlmostEqual(c.y, 4.56, places=2)
        self.assertAlmostEqual(c.radius, 7.89, places=2)

    def test_derived_circle_with_args_bad_attr(self):
        c = _CircleWithArgs()
        with self.assertRaises(AttributeError):
            # pylint: disable=attribute-defined-outside-init
            c.this_attr_is_missing = 42

    def test_derived_circle_with_explicit_args(self):
        c = _CircleWithArgs(-1.1, -2.2, 3.3)
        self.assertAlmostEqual(c.x, -1.1, places=2)
        self.assertAlmostEqual(c.y, -2.2, places=2)
        self.assertAlmostEqual(c.radius, 3.3, places=2)

    def test_derived_circle_with_property(self):
        c = _CircleWithProperties()
        c.radius = 12.34
        self.assertAlmostEqual(c.radius, 12.34, places=2)

    def test_derived_circle_with_property_bad_attr(self):
        c = _CircleWithProperties()
        with self.assertRaises(AttributeError):
            # pylint: disable=attribute-defined-outside-init
            c.this_attr_is_also_missing = 42

    def test_derived_circle_with_property_bad_type(self):
        c = _CircleWithProperties()
        with self.assertRaises(TypeError):
            c.radius = u"fail please"

    def test_derived_circle_with_property_bad_value(self):
        c = _CircleWithProperties()
        with self.assertRaises(ValueError):
            c.radius = -4.4


class _CircleArray(typesbase.CFFICDataWrapper):
    """
    Used in TestDerivedArrayTypes.
    """
    def __init__(self, size):
        cdecl = "circle_t[%i]" % size
        super(_CircleArray, self).__init__(cdecl, _ffi_with_circle_t)


class TestDerivedArrayTypes(TestCase):
    """
    Tests for types based on :class:`pywincffi.core.typesbase.CFFICDataWrapper`
    """

    def test_derived_circle_array(self):
        c = _CircleArray(4)
        for i in range(4):
            c[i].x = i
            c[i].y = 0.0
            c[i].radius = 1.5
        for i in range(4):
            self.assertAlmostEqual(c[i].x, i, places=2)
            self.assertAlmostEqual(c[i].y, 0.0, places=2)
            self.assertAlmostEqual(c[i].radius, 1.5, places=2)

    def test_derived_circle_array_out_of_bounds(self):
        c = _CircleArray(4)
        with self.assertRaises(IndexError):
            c[4].x = -9.9

    def test_derived_circle_array_bad_attr(self):
        c = _CircleArray(4)
        with self.assertRaises(AttributeError):
            c[2].crazy_missing_attr = 42
