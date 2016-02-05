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
