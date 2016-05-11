import string
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
        self.assertAlmostEqual(o.x, 123.0)
        self.assertAlmostEqual(o.y, 456.0)
        self.assertAlmostEqual(o.z, 789.0)

    def test_char_array_set_and_get(self):
        o = typesbase.CFFICDataWrapper("char [256]")
        content = string.letters
        content_len = len(content)
        for i in range(256):
            o[i] = content[i % content_len]
        for i in range(256):
            self.assertEqual(o[i], content[i % content_len])

    def test_char_array_set_and_ffi_string(self):
        ffi = cffi.FFI()
        o = typesbase.CFFICDataWrapper("char [256]")
        content = string.digits
        content_len = len(content)
        for i in range(content_len):
            o[i] = content[i]
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
            o[i].hour = i;
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
        o.uuid = '01234567-abcd-abcd-abcd-0123456789ab'
        o.fd = 0xfd
        o.type = 2
        o.u.file.inode = 12345
        o.u.file.name = 'the-filename.test'
        self.assertEqual(
            ffi.string(o.uuid),
            '01234567-abcd-abcd-abcd-0123456789ab',
        )
        self.assertEqual(o.fd, 0xfd)
        self.assertEqual(o.type, 2)
        self.assertEqual(o.u.file.inode, 12345)
        self.assertEqual(ffi.string(o.u.file.name), 'the-filename.test')

    def test_externally_provided_ffi(self):
        ffi = cffi.FFI()
        ffi.cdef("""
            typedef struct _person {
                wchar_t first_name[32];
                wchar_t last_name[32];
            } person_t;
        """)
        o = typesbase.CFFICDataWrapper("person_t *", ffi)
        o.first_name = u'First Name'
        o.last_name = u'Last Name'
        self.assertEqual(ffi.string(o.first_name), u'First Name')
        self.assertEqual(ffi.string(o.last_name), u'Last Name')

