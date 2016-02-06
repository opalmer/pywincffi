import os
import tempfile
from os.path import isfile

from pywincffi.dev.testutil import TestCase
from pywincffi.kernel32 import MoveFileEx


class TestMoveFileEx(TestCase):
    """
    Tests for :func:`pywincffi.kernel32.MoveFileEx`
    """
    def test_replaces_file(self):
        # Destination file exists, this should replace it.
        file_contents = self.random_string(12)
        fd, path1 = tempfile.mkstemp()

        with os.fdopen(fd, "w") as file_:
            file_.write(file_contents)

        fd, path2 = tempfile.mkstemp()
        self.addCleanup(os.remove, path2)
        os.close(fd)

        MoveFileEx(path1, path2)

        with open(path2, "r") as file_:
            self.assertEqual(file_.read(), file_contents)

        self.assertFalse(isfile(path1))

    def test_renames_file(self):
        # Destination file does not exist, this should create it.
        file_contents = self.random_string(12)
        fd, path1 = tempfile.mkstemp()
        path2 = path1 + ".new"

        with os.fdopen(fd, "w") as file_:
            file_.write(file_contents)

        MoveFileEx(path1, path2)

        with open(path2, "r") as file_:
            self.assertEqual(file_.read(), file_contents)

        self.assertFalse(isfile(path1))
