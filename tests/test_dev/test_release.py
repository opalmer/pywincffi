import os
import tempfile
import subprocess
import sys
from os.path import dirname, abspath, isfile, join

from pywincffi.dev.release import check_wheel
from pywincffi.dev.testutil import TestCase


class TestWheel(TestCase):
    """
    Tests for constants of :func:`pywincffi.dev.release.test_wheel`
    """
    def test_fails(self):
        fd, path = tempfile.mkstemp()
        self.addCleanup(os.remove, path)

        with os.fdopen(fd, "w") as file_:
            file_.write("")

        self.assertFalse(check_wheel(path))

    def test_success(self):
        root_dir = dirname(dirname(dirname(abspath(__file__))))

        # Be sure this exists otherwise the command below may fail for
        # unexpected reasons.
        setup_py = join(root_dir, "setup.py")
        self.assertTrue(isfile(setup_py), "%s does not exist" % setup_py)

        # Build pywincffi.  We should always be able to unpack our own
        # library and this also gives us a way to test wheel build directly.
        process = subprocess.Popen(
            [sys.executable, "setup.py", "bdist_wheel"],
            stderr=subprocess.PIPE, stdout=subprocess.PIPE, cwd=root_dir)
        process.communicate()
        self.assertEqual(process.returncode, 0)

        for root, dirs, files in os.walk(join(root_dir, "dist")):
            for filename in files:
                path = join(root, filename)
                self.assertTrue(check_wheel(path), path)