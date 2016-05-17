from pywincffi import wintypes
from pywincffi.dev.testutil import TestCase


class Test_SECURITY_ATTRIBUTES(TestCase):
    """
    Tests for :class:`pywincffi.wintypes.SECURITY_ATTRIBUTES`
    """
    def test_attr_nLength(self):
        sa = wintypes.SECURITY_ATTRIBUTES()
        self.assertGreater(sa.nLength, 0)

    def test_attr_nLength_read_only(self):
        sa = wintypes.SECURITY_ATTRIBUTES()
        with self.assertRaises(TypeError):
            sa.nLength = 1

    def test_attr_bInheritHandle_true(self):
        sa = wintypes.SECURITY_ATTRIBUTES()
        sa.bInheritHandle = True
        self.assertEqual(sa.bInheritHandle, True)

    def test_attr_bInheritHandle_false(self):
        sa = wintypes.SECURITY_ATTRIBUTES()
        sa.bInheritHandle = False
        self.assertEqual(sa.bInheritHandle, False)

    def test_missing_attr(self):
        sa = wintypes.SECURITY_ATTRIBUTES()
        with self.assertRaises(AttributeError):
            sa.no_such_attr = None


class Test_OVERLAPPED(TestCase):
    """
    Tests for :class:`pywincffi.wintypes.OVERLAPPED`
    """
    def test_attr_Offset(self):
        o = wintypes.OVERLAPPED()
        o.Offset = 12345
        self.assertEqual(o.Offset, 12345)

    def test_attr_OffsetHigh(self):
        o = wintypes.OVERLAPPED()
        o.OffsetHigh = 54321
        self.assertEqual(o.OffsetHigh, 54321)

    def test_missing_attr(self):
        o = wintypes.OVERLAPPED()
        with self.assertRaises(AttributeError):
            o.no_such_attr = None

    def test_attr_hEvent_assign(self):
        o = wintypes.OVERLAPPED()
        h = wintypes.HANDLE()
        o.hEvent = h
        self.assertIsNot(o.hEvent, h)
        self.assertEqual(o.hEvent, h)


class Test_FILETIME(TestCase):
    """
    Tests for :class:`pywincffi.wintypes.FILETIME`
    """
    def test_attr_dwLowDateTime(self):
        ft = wintypes.FILETIME()
        ft.dwLowDateTime = 42
        self.assertEqual(ft.dwLowDateTime, 42)

    def test_attr_dwHighDateTime(self):
        ft = wintypes.FILETIME()
        ft.dwHighDateTime = 24
        self.assertEqual(ft.dwHighDateTime, 24)

    def test_missing_attr(self):
        ft = wintypes.FILETIME()
        with self.assertRaises(AttributeError):
            ft.no_such_attr = None

