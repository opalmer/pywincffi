import os
import hashlib
import tempfile
import shutil
import string
import subprocess
import sys
from random import randint, choice
from textwrap import dedent
from os.path import dirname, abspath, isfile, join, isdir, basename

try:
    from http.client import OK, BAD_REQUEST
except ImportError:
    # pylint: disable=import-error,wrong-import-order
    from httplib import OK, BAD_REQUEST

from mock import Mock, patch
from github import Github
from requests.adapters import HTTPAdapter

from pywincffi.core.config import config
from pywincffi.dev import release  # used to mock top level functions
from pywincffi.dev.release import (
    Session, AppVeyor, AppVeyorArtifact, GitHubAPI, check_wheel, docs_built)
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

    def test_ignore_coverage(self):
        artifacts = [
            {"type": "File", "fileName": ".coverage"}
        ]

        _download = Session.download
        self.artifact_path = None
        self.artifact_url = None

        def download(_, url, path=None):
            _download(TestSession.DOWNLOAD_URL, path=path)

        with patch.object(Session, "json", return_value=artifacts):
            with patch.object(Session, "download", download):
                for _ in self.appveyor.artifacts():
                    self.fail("There should be nothing to iterate over")

    def test_checks_wheel(self):
        artifacts = [
            {"type": "File", "fileName": "foobar.whl"}
        ]

        _download = Session.download
        self.artifact_path = None
        self.artifact_url = None
        directory = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, directory, ignore_errors=True)

        def download(_, url, path=None):
            _download(TestSession.DOWNLOAD_URL, path=path)

        with patch.object(release, "check_wheel") as mocked:
            with patch.object(Session, "json", return_value=artifacts):
                with patch.object(Session, "download", download):
                    list(self.appveyor.artifacts(directory=directory))

        mocked.assert_called_with(join(directory, "foobar.whl"))


class GitHubAPICase(TestCase):
    """
    The base class for all test cases of :class:`GitHubAPI`.  This is
    required so that the tests don't require an authentication
    token and so we can avoid hitting GitHub's API.
    """
    def setUp(self):
        super(GitHubAPICase, self).setUp()
        self.version = "0.0.0"

        # The test token
        self.token = "fake_token"
        github_token = config.get("pywincffi", "github_token")
        config.set("pywincffi", "github_token", self.token)
        self.addCleanup(config.set, "pywincffi", "github_token", github_token)

        # Mocks for the Github class so we don't make any API calls
        self.mocked_get_repo = patch.object(
            Github, "get_repo",
            return_value=Mock(
                get_milestones=lambda: [Mock(title=self.version)]))
        self.mocked_get_repo.start()
        self.addCleanup(self.mocked_get_repo.stop)


class TestGitHubAPIInit(GitHubAPICase):
    """
    Tests for :meth:`pywincffi.dev.release.GitHubAPI.__init__`
    """
    def test_version(self):
        api = GitHubAPI(self.version)
        self.assertEqual(api.version, self.version)

    def test_branch_default(self):
        api = GitHubAPI(self.version)
        self.assertEqual(api.branch, "master")

    def test_branch_non_default(self):
        api = GitHubAPI(self.version, branch="foobar")
        self.assertEqual(api.branch, "foobar")

    def test_token_not_set(self):
        config.set("pywincffi", "github_token", "")
        with self.assertRaises(RuntimeError):
            GitHubAPI(self.version)

    def test_milestone_not_found(self):
        self._cleanups.remove((self.mocked_get_repo.stop, (), {}))
        self.mocked_get_repo.stop()
        mock = patch.object(
            Github, "get_repo",
            return_value=Mock(
                get_milestones=lambda: [Mock(title="x.x.x")]))
        mock.start()
        self.addCleanup(mock.stop)
        with self.assertRaises(ValueError):
            GitHubAPI(self.version)


class TestGitHubAPICommit(GitHubAPICase):
    """
    Tests for :meth:`pywincffi.dev.release.GitHubAPI.commit`
    """
    def test_commit(self):
        api = GitHubAPI(self.version)
        expected = "da39a3ee5e6b4b0d3255bfef95601890afd80709"
        with patch.object(
            api.repo, "get_branch", return_value=Mock(
                commit=Mock(sha=expected))):
            self.assertEqual(api.commit(), expected)


class TestGitHubAPIReleaseMessage(GitHubAPICase):
    """
    Tests for :meth:`pywincffi.dev.release.GitHubAPI.release_message`
    """
    def test_gets_all_issues(self):
        api = GitHubAPI(self.version)

        with patch.object(api.repo, "get_issues", return_value=[]) as mocked:
            api.release_message()

        mocked.assert_called_with(milestone=api.milestone, state="all")

    def test_message(self):
        issues = [
            Mock(number=1, url="/1", title="Issue 1", state="closed",
                 labels=[Mock(name="unittest")]),
            Mock(number=3, url="/3", title="Issue 3", state="closed",
                 labels=[Mock(name="enhancement")]),
            Mock(number=2, url="/2", title="Issue 2", state="closed",
                 labels=[Mock(name="enhancement")]),
            Mock(number=4, url="/4", title="Issue 4", state="closed",
                 labels=[Mock(name="bug")]),
            Mock(number=5, url="/5", title="Issue 5", state="closed",
                 labels=[Mock(name="enhancement"), Mock(name="bug")]),
            Mock(number=6, url="/6", title="Issue 6", state="closed",
                 labels=[])
        ]

        api = GitHubAPI(self.version)
        with patch.object(api.repo, "get_issues", Mock(return_value=issues)):
            self.assertEqual(api.release_message().strip(), dedent("""
        ## External Links
        Links for documentation, release files and other useful information.
        * [Documentation](%s)
        * [PyPi Package](%s)
        * [GitHub Issues](%s)

        ## Pull Requests and Issues
        Pull requests and issues associated with this release.

        #### Other
        [6](/6) - Issue 6
        [5](/5) - Issue 5
        [4](/4) - Issue 4
        [2](/2) - Issue 2
        [3](/3) - Issue 3
        [1](/1) - Issue 1
            """).strip() % (
                api.read_the_docs, api.pypi_release, api.milestone_filter))


class TestGitHubAPICreateRelease(GitHubAPICase):
    """
    Tests for :meth:`pywincffi.dev.release.GitHubAPI.create_release`
    """
    def setUp(self):
        super(TestGitHubAPICreateRelease, self).setUp()
        self.api = GitHubAPI(self.version)
        mock = patch.object(self.api, "release_message", return_value="foobar")
        mock.start()
        self.addCleanup(mock.stop)

    def set_releases(self, value):
        mock = patch.object(self.api.repo, "get_releases", return_value=value)
        mock.start()
        self.addCleanup(mock.stop)
        return mock

    def test_dry_run(self):
        self.set_releases([])

        # Exceptions will be raised if dry_run actually tries to do
        # something
        self.assertEqual(self.api.create_release(dry_run=True), "foobar")

    def test_closes_milestone(self):
        self.set_releases([])

        with patch.object(self.api.milestone, "edit") as mocked:
            self.api.create_release(close_milestone=True)

        mocked.assert_called_with(self.version, state="closed")

    def test_create_tag_and_release_fails_without_recreate(self):
        self.set_releases([Mock(tag_name=self.version)])

        with self.assertRaisesRegex(RuntimeError,
                                    ".*%r already exists.*" % self.version):
            self.api.create_release()

    def test_create_tag_and_release_deletes_existing(self):
        release_tag = Mock(tag_name=self.version)
        self.set_releases([release_tag])
        self.api.create_release(recreate=True)
        self.assertEqual(release_tag.delete_release.call_count, 1)

    def test_create_tag_and_release_arguments(self):
        self.set_releases([])

        with patch.object(self.api.repo,
                          "create_git_tag_and_release") as mocked:
            self.api.create_release(recreate=True)

        mocked.assert_called_with(
            self.api.version,
            "Tagged by release.py",
            self.version,
            self.api.release_message(),
            self.api.commit(),
            "commit",
            draft=True, prerelease=False
        )


class TestDocsBuilt(TestCase):
    """
    Tests for :func:`pywincffi.dev.release.GitHubAPI.docs_built`
    """
    def test_success(self):
        self.assertTrue(docs_built("latest"))

    def test_failure(self):
        self.assertFalse(docs_built("does_not_exist"))
