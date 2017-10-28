#!/usr/bin/env python

from __future__ import with_statement

import argparse
import logging
import os
import subprocess
import sys
from os.path import dirname, abspath, join, expanduser

try:
    WindowsError
except NameError:  # pragma: no cover
    WindowsError = OSError

import requests

ROOT = dirname(dirname(abspath(__file__)))

# Add the root of the repo to sys.path so
# we can import pywcinffi directly.
sys.path.insert(0, ROOT)

from pywincffi import __version__
from pywincffi.core.logger import get_logger, STREAM_HANDLER
from pywincffi.dev.release import GitHubAPI, AppVeyor, docs_built

APPVEYOR_API = "https://ci.appveyor.com/api"
APPVEYOR_API_PROJ = APPVEYOR_API + "/projects/opalmer/pywincffi"

session = requests.Session()
session.headers.update({
    "Accept": "application/json",
    "Content-Type": "application/json"
})

logger = get_logger("dev.release")
logging.basicConfig(
    level=logging.INFO,
    handlers=[STREAM_HANDLER]
)


def should_continue(question, skip=False):
    """
    Asks a question, returns True if the answer is yes.  Calls
    ``sys.exit(1) if not."""
    if skip:
        print("%s < 'y'" % question)
        return True

    try:
        answer = raw_input(question)
    except NameError:
        answer = input(question)

    if answer != "y":
        print("Stopping.")
        sys.exit(1)


def parse_arguments():
    """Constructs an argument parser and returns parsed arguments"""
    parser = argparse.ArgumentParser(description="Cuts a release of pywincffi")
    parser.add_argument(
        "--confirm", action="store_true", default=False,
        help="If provided, do not ask any questions and answer 'yes' to all "
             "queries."
    )
    parser.add_argument(
        "-n", "--dry-run", action="store_true", default=False,
        help="If provided, don't do anything destructive."
    )
    parser.add_argument(
        "--skip-pypi", action="store_true", default=False,
        help="If provided, do not upload the release to pypi."
    )
    parser.add_argument(
        "--skip-github", action="store_true", default=False,
        help="If provided, do not create a release on GitHub."
    )
    parser.add_argument(
        "--keep-milestone-open", action="store_true", default=False,
        help="If provided, do not close the milestone"
    )
    parser.add_argument(
        "--download-artifacts",
        help="If provided, download artifacts to this directory.  The setup.py "
             "will redownload the files, this is mostly for testing."
    )
    parser.add_argument(
        "--recreate", action="store_true", default=False,
        help="If provided, recreate the release"
    )
    parser.add_argument(
        "--github-token", default=None,
        help="The token to use to connect to github"
    )
    args = parser.parse_args()

    if not args.github_token:
        try:
            with open(join(expanduser("~"), ".github_token")) as file_:
                args.github_token = file_.read().strip()
        except (OSError, IOError, WindowsError):
            args.github_token = os.environ.get("GITHUB_TOKEN")

    if not args.github_token:
        parser.error(
            "No GitHub token located in --github-token, ~/.github_token or "
            "$GITHUB_TOEKN")

    return args


def main():
    args = parse_arguments()
    version = ".".join(map(str, __version__))

    # Make sure we really want to create a release of this version.
    should_continue(
        "Create release of version %s? [y/n] " % version,
        skip=args.confirm
    )

    if not args.skip_github:
        github = GitHubAPI(version, token=args.github_token)

        if github.milestone.state != "closed":
            should_continue(
                "GitHub milestone %s is still open, continue? [y/n] " % version,
                skip=args.confirm)

        release = github.create_release(
            recreate=args.recreate, dry_run=args.dry_run,
            close_milestone=not args.keep_milestone_open)

        if args.dry_run:
            print(release)

        # TODO: Hack around in PyGitHub's request context so we can
        # upload release artifacts
        logger.warning("You must manually upload release artifacts")

        logger.info("Created GitHub release")

    if args.download_artifacts:
        appveyor = AppVeyor()
        for _ in appveyor.artifacts(directory=args.download_artifacts):
            continue

        logger.info("Downloaded build artifacts to %s", args.download_artifacts)

    if not args.skip_pypi:
        subprocess.check_call([
            sys.executable, "setup.py", "register"],
            cwd=ROOT
        )
        subprocess.check_call([
            sys.executable, "setup.py", "upload_from_appveyor"],
            cwd=ROOT
        )
        logger.info("Created PyPi release")

    if not docs_built(version):
        logger.error("Documentation not built for %s", version)


if __name__ == "__main__":
    main()
