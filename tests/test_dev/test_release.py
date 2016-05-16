import os
import hashlib
import tempfile
import shutil
import string
import subprocess
import sys
from collections import namedtuple
from random import randint, choice, shuffle
from os.path import dirname, abspath, isfile, join, isdir, basename

try:
    from http.client import OK, BAD_REQUEST
except ImportError:
    # pylint: disable=import-error,wrong-import-order
    from httplib import OK, BAD_REQUEST

from mock import Mock, patch
from requests.adapters import HTTPAdapter

from pywincffi.core.config import config
from pywincffi.dev import release  # used to mock top level functions
from pywincffi.dev.release import (
    Session, AppVeyor, AppVeyorArtifact, GitHubAPI, Issue,
    check_wheel, docs_built)
from pywincffi.dev.testutil import TestCase


def random_string():
    return "".join(
        [choice(string.ascii_letters) for _ in range(randint(5, 20))])


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


class TestDownloadBase(TestCase):
    REQUIRES_INTERNET = True
    COMMIT = "fff6dff13502f7431210cbd8b1f64e2e4eea6475"
    DOWNLOAD_SHA1 = "b34ffce316e11eebc5b2ceb4398a9606630c72bf"
    DOWNLOAD_URL = \
        "https://raw.githubusercontent.com/opalmer/pywincffi/" \
        "%s/.ci/appveyor/run_with_compiler.cmd" % COMMIT


class TestSession(TestDownloadBase):
    """
    Tests for constants of :class:`pywincffi.dev.release.Session`
    """
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
        try:
            path = Session.download(self.DOWNLOAD_URL)
        except RuntimeError as error:
            if "Got 404 Not Found instead" in error.args[0]:
                self.fail("Remote branch appears to be missing")
            raise

        self.addCleanup(os.remove, path)
        with open(path, "rb") as file_:
            sha1 = hashlib.sha1(file_.read())

        self.assertEqual(sha1.hexdigest(), self.DOWNLOAD_SHA1)

    def test_download_specific_path(self):
        fd, path = tempfile.mkstemp()
        os.close(fd)
        self.addCleanup(os.remove, path)

        try:
            Session.download(self.DOWNLOAD_URL, path=path)
        except RuntimeError as error:
            if "Got 404 Not Found instead" in error.args[0]:
                self.fail("Remote branch appears to be missing")
            raise

        with open(path, "rb") as file_:
            sha1 = hashlib.sha1(file_.read())

        self.assertEqual(sha1.hexdigest(), self.DOWNLOAD_SHA1)


class TestAppVeyor(TestDownloadBase):
    """
    Tests for constants of :class:`pywincffi.dev.release.AppVeyor`
    """
    def setUp(self):
        super(TestAppVeyor, self).setUp()
        self.job_id = random_string()
        self.artifact_url = None
        self.artifact_path = None
        self.branch = {
            "build": {
                "message": random_string(),
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

    def test_creates_directory(self):
        path = join(tempfile.gettempdir(), random_string())

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
            {"type": "File", "fileName": basename(self.DOWNLOAD_URL)}
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

            _download(self.DOWNLOAD_URL, path=path)

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
            _download(self.DOWNLOAD_URL, path=path)

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
            _download(self.DOWNLOAD_URL, path=path)

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

        # The test token.  This ensures that we're never going to
        # use a valid token which could cause problems on GitHub if
        # used.
        self.token = "fake_token"
        github_token = config.get("pywincffi", "github_token")
        config.set("pywincffi", "github_token", self.token)
        self.addCleanup(config.set, "pywincffi", "github_token", github_token)

    # NOTE: `branch` should match the default
    def api(self, version=None, branch=None, repo=None, milestones=None,
            releases=None):
        if version is None:
            version = self.version

        if milestones is None:
            milestones = [Mock(title=self.version)]

        if releases is None:
            releases = [Mock(tag_name=self.version)]

        if repo is None:
            repo = Mock(
                get_milestones=Mock(return_value=milestones),
                get_releases=Mock(return_value=releases)
            )

        return GitHubAPI(version, branch=branch, repo_=repo)


class TestGitHubAPIInit(GitHubAPICase):
    """
    Tests for :meth:`pywincffi.dev.release.GitHubAPI.__init__`
    """
    def test_version(self):
        api = self.api(version=self.version)
        self.assertEqual(api.version, self.version)

    def test_branch_default(self):
        api = self.api()
        self.assertEqual(api.branch, "master")

    def test_branch_non_default(self):
        api = self.api(version=self.version, branch="foobar")
        self.assertEqual(api.branch, "foobar")

    def test_token_not_set(self):
        config.set("pywincffi", "github_token", "")
        with self.assertRaises(RuntimeError):
            self.api()

    def test_milestone_not_found(self):
        with self.assertRaises(ValueError):
            self.api(version=self.version, milestones=[])

    def test_looks_for_milestones_with_all_states(self):
        api = self.api()

        # pylint: disable=no-member
        api.repo.get_milestones.assert_called_with(state="all")


class TestGitHubAPICommit(GitHubAPICase):
    """
    Tests for :meth:`pywincffi.dev.release.GitHubAPI.commit`
    """
    def test_commit(self):
        expected = "da39a3ee5e6b4b0d3255bfef95601890afd80709"
        api = self.api()
        api.repo.get_branch.return_value = Mock(commit=Mock(sha=expected))
        self.assertEqual(api.commit(), expected)

        # pylint: disable=no-member
        api.repo.get_branch.assert_called_with(api.branch)

FakeLabel = namedtuple("FakeLabel", ("name", ))


class FakeIssue(object):
    def __init__(self, type_=None, state=None, labels=None):
        if type_ is None:
            type_ = choice(["pull", "issue"])
        if state is None:
            state = choice(["closed", "open"])

        self.type_ = type_
        self.number = randint(1, 1024)
        self.title = random_string()
        self.labels = []
        self.state = state

        if labels is None:
            for _ in range(randint(1, 5)):
                self.labels.append(
                    FakeLabel(choice(
                        ["bug", "enhancement", "unittest", "documentation"])))
        else:
            for label in labels:
                self.labels.append(FakeLabel(label))

    @property
    def html_url(self):
        if self.type_ == "pull":
            url = "https://github.com/opalmer/pywincffi/pull/{number}"
        else:
            url = "https://github.com/opalmer/pywincffi/issues/{number}"
        return url.format(number=self.number)


class GitHubAPICaseWithIssues(GitHubAPICase):
    # pylint: disable=arguments-differ
    def api(self, version=None, branch=None, repo=None, milestones=None,
            issues=None, releases=None):
        api = super(GitHubAPICaseWithIssues, self).api(
            version=version, branch=branch, repo=repo, milestones=milestones,
            releases=releases)
        default_issues = [
            FakeIssue(), FakeIssue(), FakeIssue(),
            FakeIssue(), FakeIssue(), FakeIssue()
        ]
        if issues is not None:
            default_issues.extend(issues)

        shuffle(default_issues)
        api.repo.get_issues = Mock(return_value=default_issues)
        return api


class TestGitHubAPIIssues(GitHubAPICaseWithIssues):
    """
    Tests for :meth:`pywincffi.dev.release.GitHubAPI.issues`
    """
    def test_get_issues_keywords(self):
        api = self.api()
        list(api.issues())

        # pylint: disable=no-member
        api.repo.get_issues.assert_called_with(
            milestone=api.milestone, state="all")

    def test_return_type(self):
        api = self.api()
        self.assertIsInstance(list(api.issues()), list)

    def test_return_type_value(self):
        api = self.api()
        for issue in api.issues():
            self.assertIsInstance(issue, Issue)

    def test_issue(self):
        api = self.api()

        for issue in api.issues():
            self.assertIsInstance(issue.issue, FakeIssue)

    def test_closed(self):
        api = self.api(issues=[FakeIssue(state="closed")])

        for issue in api.issues():
            self.assertEqual(issue.closed, issue.issue.state == "closed")

    def issue_type(self):
        api = self.api(issues=[
            FakeIssue(labels=["enhancement"]), FakeIssue(labels=["bug"]),
            FakeIssue(labels=["refactor"])
        ])

        for issue in api.issues():
            if "refactor" in issue.labels:
                expected_issue_type = "refactor"

            elif "bug" in issue.labels:
                expected_issue_type = "bugs"

            elif "enhancement" in issue.labels:
                expected_issue_type = "enhancements"

            elif "documentation" in issue.labels:
                expected_issue_type = "documentation"

            elif "unittest" in issue.labels:
                expected_issue_type = "unittests"

            else:
                expected_issue_type = "other"

            self.assertEqual(issue.type, expected_issue_type)

    def test_labels(self):
        api = self.api(issues=[FakeIssue(labels=["foo"])])

        for issue in api.issues():
            self.assertEqual(
                issue.labels,
                set(label.name for label in issue.issue.labels))

    def test_issue_url(self):
        api = self.api()

        for issue in api.issues():
            self.assertEqual(issue.issue.html_url, issue.url)


class TestGitHubAPIReleaseMessage(GitHubAPICaseWithIssues):
    """
    Tests for :meth:`pywincffi.dev.release.GitHubAPI.release_message`

    .. note::

        This is not a full test because most of the testing is completed
        in TestGitHubAPIIssues() above.
    """
    def test_return_type(self):
        api = self.api()
        self.assertIsInstance(api.release_message(), str)

    def test_doc_link(self):
        api = self.api(releases=[])
        self.assertIn(
            "* [Documentation](%s)" % api.read_the_docs,
            api.release_message())

    def test_pypi_link(self):
        api = self.api()
        self.assertIn(
            "* [PyPi Package](%s)" % api.pypi_release,
            api.release_message())

    def test_github_issues(self):
        api = self.api()
        self.assertIn(
            "* [GitHub Issues](%s)" % api.milestone_filter,
            api.release_message())

    def test_fails_for_extra_types(self):
        issue = FakeIssue()

        # pylint: disable=attribute-defined-outside-init
        issue.type = "some_new_type"

        api = self.api()
        with patch.object(api, "issues", return_value=[issue]):
            with self.assertRaises(ValueError):
                api.release_message()

    def test_contains_issue_links(self):
        api = self.api()
        release_message = api.release_message()
        for issue in api.issues():
            text = "[{number}]({url}) - {title}".format(
                number=issue.number, url=issue.url, title=issue.title
            )
            self.assertIn(text, release_message)


class TestGitHubAPICreateRelease(GitHubAPICaseWithIssues):
    """
    Tests for :meth:`pywincffi.dev.release.GitHubAPI.create_release`
    """
    def test_dry_run(self):
        api = self.api()
        api.create_release(dry_run=True)
        self.assertEqual(api.milestone.edit.call_count, 0)

    def test_closes_milestone(self):
        api = self.api(releases=[])
        api.create_release(close_milestone=True)
        api.milestone.edit.assert_called_with(api.version, state="closed")

    def test_create_tag_and_release_fails_without_recreate(self):
        api = self.api()
        with self.assertRaisesRegex(RuntimeError,
                                    ".*%r already exists.*" % self.version):
            api.create_release()

    def test_create_tag_and_release_deletes_existing(self):
        api = self.api()
        api.create_release(recreate=True)

        # pylint: disable=no-member
        get_releases = api.repo.get_releases.return_value[0]
        get_releases.delete_release.assert_called_with()

    def test_create_tag_and_release_arguments(self):
        api = self.api()
        api.create_release(recreate=True)

        # pylint: disable=no-member
        api.repo.create_git_tag_and_release.assert_called_with(
            api.version,
            "Tagged by release.py",
            api.version,
            api.release_message(),
            api.commit(),
            "commit",
            draft=True, prerelease=False
        )


class TestDocsBuilt(TestCase):
    """
    Tests for :func:`pywincffi.dev.release.GitHubAPI.docs_built`
    """
    REQUIRES_INTERNET = True

    def test_success(self):
        self.assertTrue(docs_built("latest"))

    def test_failure(self):
        self.assertFalse(docs_built("does_not_exist"))
