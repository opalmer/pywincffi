from pywincffi.dev.testutil import TestCase
from pywincffi.wintypes import (
    HANDLE, SECURITY_ATTRIBUTES, OVERLAPPED, FILETIME)


class TestSECURITY_ATTRIBUTES(TestCase):
    """
    Tests for :class:`pywincffi.wintypes.SECURITY_ATTRIBUTES`
    """
    def test_attr_nLength(self):
        sa = SECURITY_ATTRIBUTES()
        self.assertGreater(sa.nLength, 0)

    def test_attr_nLength_read_only(self):
        sa = SECURITY_ATTRIBUTES()
        with self.assertRaises(TypeError):
            sa.nLength = 1

    def test_attr_bInheritHandle_true(self):
        sa = SECURITY_ATTRIBUTES()
        sa.bInheritHandle = True
        self.assertEqual(sa.bInheritHandle, True)

    def test_attr_bInheritHandle_false(self):
        sa = SECURITY_ATTRIBUTES()
        sa.bInheritHandle = False
        self.assertEqual(sa.bInheritHandle, False)

    def test_missing_attr(self):
        sa = SECURITY_ATTRIBUTES()
        with self.assertRaises(AttributeError):
            sa.no_such_attr = None


class TestOVERLAPPED(TestCase):
    """
    Tests for :class:`pywincffi.wintypes.OVERLAPPED`
    """
    def test_attr_Offset(self):
        o = OVERLAPPED()
        o.Offset = 12345
        self.assertEqual(o.Offset, 12345)

    def test_attr_OffsetHigh(self):
        o = OVERLAPPED()
        o.OffsetHigh = 54321
        self.assertEqual(o.OffsetHigh, 54321)

    def test_missing_attr(self):
        o = OVERLAPPED()
        with self.assertRaises(AttributeError):
            o.no_such_attr = None

    def test_attr_hEvent_assign(self):
        o = OVERLAPPED()
        h = HANDLE()
        o.hEvent = h
        self.assertIsNot(o.hEvent, h)
        self.assertEqual(o.hEvent, h)

    def test_attr_hEvent_assign_wrong_type(self):
        o = OVERLAPPED()
        with self.assertRaises(TypeError):
            o.hEvent = None


class TestFILETIME(TestCase):
    """
    Tests for :class:`pywincffi.wintypes.FILETIME`
    """
    def test_attr_dwLowDateTime(self):
        ft = FILETIME()
        ft.dwLowDateTime = 42
        self.assertEqual(ft.dwLowDateTime, 42)

    def test_attr_dwHighDateTime(self):
        ft = FILETIME()
        ft.dwHighDateTime = 24
        self.assertEqual(ft.dwHighDateTime, 24)

    def test_missing_attr(self):
        ft = FILETIME()
        with self.assertRaises(AttributeError):
            ft.no_such_attr = None
