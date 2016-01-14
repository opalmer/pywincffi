import os
import hashlib
import tempfile
import subprocess
import sys
from os.path import dirname, abspath, isfile, join

try:
    from http.client import OK, BAD_REQUEST
except ImportError:
    # pylint: disable=import-error,wrong-import-order
    from httplib import OK, BAD_REQUEST

from requests.adapters import HTTPAdapter

from pywincffi.dev.release import Session, AppVeyor, check_wheel
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

        wheels = []

        while not wheels:
            for root, _, files in os.walk(join(root_dir, "dist")):
                for filename in files:
                    if filename.endswith(".whl"):
                        wheels.append(join(root, filename))

            if wheels:
                break

            # Build pywincffi if we need to. We should always be able to
            # unpack our own library.
            process = subprocess.Popen(
                [sys.executable, "setup.py", "bdist_wheel"],
                stderr=subprocess.PIPE, stdout=subprocess.PIPE, cwd=root_dir)
            process.communicate()
            self.assertEqual(process.returncode, 0)

        for path in wheels:
            self.assertTrue(check_wheel(path), path)


class TestSession(TestCase):
    DOWNLOAD_SHA1 = "89ff14348b410051fff2eb206183993f659d85e0"
    DOWNLOAD_URL = "https://raw.githubusercontent.com/opalmer/pywincffi/" \
                    "master/.ci/appveyor/run_with_compiler.cmd"

    def setUp(self):
        super(TestSession, self).setUp()
        self.session = Session.session
        self.session.mount("https://", HTTPAdapter(max_retries=100))

    def test_check_code_success(self):
        response = self.session.get(AppVeyor.API)
        Session.check_code(response, OK)

    def test_check_code_failure(self):
        response = self.session.get(AppVeyor.API)

        with self.assertRaises(RuntimeError):
            Session.check_code(response, BAD_REQUEST)

    def test_json_success(self):
        data = Session.json(AppVeyor.API_PROJECT)
        self.assertEqual(data.get("project", {}).get("name", {}), "pywincffi")

    def test_json_failure(self):
        with self.assertRaises(ValueError):
            Session.json(AppVeyor.API)

    def test_download_random_path(self):
        path = Session.download(self.DOWNLOAD_URL)
        self.addCleanup(os.remove, path)
        with open(path, "rb") as file_:
            sha1 = hashlib.sha1(file_.read())

        self.assertEqual(sha1.hexdigest(), self.DOWNLOAD_SHA1)

    def test_download_specific_path(self):
        fd, path = tempfile.mkstemp()
        os.close(fd)
        self.addCleanup(os.remove, path)

        Session.download(self.DOWNLOAD_URL, path=path)
        with open(path, "rb") as file_:
            sha1 = hashlib.sha1(file_.read())

        self.assertEqual(sha1.hexdigest(), self.DOWNLOAD_SHA1)
