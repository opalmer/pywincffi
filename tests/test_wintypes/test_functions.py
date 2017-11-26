# -*- coding: utf-8 -*-

import os
import socket
import tempfile
from errno import EBADF

from pywincffi.core import dist
from pywincffi.dev.testutil import TestCase
from pywincffi.exceptions import InputError
from pywincffi.kernel32 import CloseHandle
from pywincffi.wintypes import SOCKET, handle_from_file, socket_from_object

try:
    WindowsError
except NameError:  # pragma: no cover
    WindowsError = OSError  # pylint: disable=redefined-builtin


class TestGetHandleFromFile(TestCase):
    """
    Tests for :func:`pywincffi.wintypes.handle_from_file`
    """
    def test_fails_if_not_a_file(self):
        with self.assertRaises(InputError):
            handle_from_file(0)

    def test_fails_if_file_is_not_open(self):
        fd, path = tempfile.mkstemp()
        self.addCleanup(os.unlink, path)
        test_file = os.fdopen(fd, "r")
        test_file.close()

        with self.assertRaises(InputError):
            handle_from_file(test_file)

    def test_opens_correct_file_handle(self):
        fd, path = tempfile.mkstemp()
        self.addCleanup(os.unlink, path)
        os.close(fd)

        test_file = open(path, "w")
        handle = handle_from_file(test_file)

        CloseHandle(handle)

        # If CloseHandle() was passed the same handle
        # that test_file is trying to write to the file
        # and/or flushing it should fail.
        try:
            test_file.write("foo")
            test_file.flush()
        except (OSError, IOError, WindowsError) as error:
            # EBADF == Bad file descriptor (because CloseHandle closed it)
            self.assertEqual(error.errno, EBADF)
        else:
            self.fail("Expected os.close(%r) to fail" % fd)


class TestSocketFromObject(TestCase):
    """
    Tests for :func:`pywincffi.wintypes.socket_from_object`
    """
    def setUp(self):
        super(TestSocketFromObject, self).setUp()
        self.python_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addCleanup(self.close)

    def close(self):
        try:
            self.python_socket.close()
        except Exception:  # pylint: disable=broad-except
            pass

    def test_type(self):
        with self.assertRaises(InputError):
            socket_from_object(None)

    def test_error_if_socket_is_closed(self):
        self.python_socket.close()
        with self.assertRaises(InputError):
            socket_from_object(self.python_socket)

    def test_return_type(self):
        sock = socket_from_object(self.python_socket)
        self.assertIsInstance(sock, SOCKET)

    def test_closesocket_success(self):
        sock = socket_from_object(self.python_socket)
        _, library = dist.load()
        self.assertEqual(library.closesocket(sock._cdata[0]), 0)

    def test_closesocket_failure(self):
        sock = socket_from_object(self.python_socket)
        self.python_socket.close()
        _, library = dist.load()

        # Socket is already closed so closesocket should fail.
        self.assertEqual(library.closesocket(sock._cdata[0]), -1)

        self.assert_last_error(library.WSAENOTSOCK)
