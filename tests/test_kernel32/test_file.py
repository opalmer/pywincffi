import os
import tempfile
from os.path import join

from pywincffi.dev.testutil import TestCase
from pywincffi.kernel32 import MoveFileEx


class TestMoveFileEx(TestCase):
    """
    Tests for :func:`pywincffi.kernel32.MoveFileEx`
    """
    def test_renames_file(self):
        tempdir = tempfile.gettempdir()
        source_filename = self.random_string(7)
        dest_filename = self.random_string(7)
        data = self.random_string(7)
        self.addCleanup(os.remove, dest_filename)

        source = join(tempdir, source_filename)

        with open(source, "w") as file_:
            file_.write(data)

        MoveFileEx(source, dest_filename)

        with open(dest_filename) as file_:
            self.assertEqual(file_.read(), data)

    def test_replaces_file(self):
        tempdir = tempfile.gettempdir()
        source_filename = self.random_string(7)
        dest_filename = self.random_string(7)
        data = self.random_string(7)
        self.addCleanup(os.remove, dest_filename)

        source = join(tempdir, source_filename)

        with open(source, "w") as file_:
            file_.write(data)

        with open(dest_filename, "w") as dest_:
            dest_.write("foobar")

        MoveFileEx(source, dest_filename)

        with open(dest_filename) as file_:
            self.assertEqual(file_.read(), data)

    # TODO: tests for directory moves
    # TODO: tests where lpNewFileName is None (NULL)

    # TODO: figure out why this does not work when running in PyCharm (but does
    # with nosetests and in an interpreter)
    def test_foo(self):
        fd1, path1 = tempfile.mkstemp()
        os.close(fd1)

        fd2, path2 = tempfile.mkstemp()
        os.close(fd2)
        MoveFileEx(path1, path2)
