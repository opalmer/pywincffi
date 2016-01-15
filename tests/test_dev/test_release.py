import os
import hashlib
import tempfile
import shutil
import string
import subprocess
import sys
from random import randint, choice
from os.path import dirname, abspath, isfile, join, isdir, basename

try:
    from http.client import OK, BAD_REQUEST
except ImportError:
    # pylint: disable=import-error,wrong-import-order
    from httplib import OK, BAD_REQUEST

from mock import patch
from requests.adapters import HTTPAdapter

from pywincffi.dev.release import (
    Session, AppVeyor, AppVeyorArtifact, check_wheel)
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
    """
    Tests for constants of :class:`pywincffi.dev.release.Session`
    """
    DOWNLOAD_SHA1 = "89ff14348b410051fff2eb206183993f659d85e0"
    DOWNLOAD_URL = \
        "https://raw.githubusercontent.com/opalmer/pywincffi/" \
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


class TestAppVeyor(TestCase):
    """
    Tests for constants of :class:`pywincffi.dev.release.AppVeyor`
    """
    def setUp(self):
        super(TestAppVeyor, self).setUp()
        self.job_id = self.random_string()
        self.artifact_url = None
        self.artifact_path = None
        self.branch = {
            "build": {
                "message": self.random_string(),
                "jobs": [
                    {
                        "jobId": self.job_id,
                        "status": "success"
                    }
                ]
            }
        }

        with patch.object(Session, "json", return_value=self.branch):
            self.appveyor = AppVeyor()

    def random_string(self):
        return "".join(
            [choice(string.ascii_letters) for _ in range(randint(5, 20))])

    def json(self):
        return None

    def test_creates_directory(self):
        path = join(tempfile.gettempdir(), self.random_string())

        with patch.object(Session, "json", return_value=[]):
            list(self.appveyor.artifacts(directory=path))

        self.assertTrue(isdir(path))
        self.addCleanup(shutil.rmtree, path, ignore_errors=True)

    def test_fails_for_unsuccessful_build(self):
        self.appveyor.branch["build"]["jobs"][0]["status"] = "foo"

        with self.assertRaises(RuntimeError):
            with patch.object(Session, "json", return_value=[]):
                list(self.appveyor.artifacts())

    def test_downloads_artifacts(self):
        artifacts = [
            {"type": "File", "fileName": basename(TestSession.DOWNLOAD_URL)}
        ]

        _download = Session.download
        self.artifact_path = None
        self.artifact_url = None

        def download(_, url, path=None):
            expected_url = \
                AppVeyor.API + \
                "/buildjobs/{id}/artifacts".format(id=self.job_id) + \
                "/" + artifacts[0]["fileName"]
            self.assertEqual(url, expected_url)
            self.artifact_path = path
            self.artifact_url = expected_url

            _download(TestSession.DOWNLOAD_URL, path=path)

        with patch.object(Session, "json", return_value=artifacts):
            with patch.object(Session, "download", download):
                results = list(self.appveyor.artifacts())

        self.assertEqual(
            results, [
                AppVeyorArtifact(
                    path=self.artifact_path,
                    url=self.artifact_url,
                    unpacked=True, build_success=True
                )
            ]
        )
