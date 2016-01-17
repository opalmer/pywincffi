#!/usr/bin/env python

from __future__ import with_statement

import argparse
import subprocess
import sys
from os.path import dirname, abspath

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
from pywincffi.core.logger import get_logger
from pywincffi.dev.release import GitHubAPI, docs_built

APPVEYOR_API = "https://ci.appveyor.com/api"
APPVEYOR_API_PROJ = APPVEYOR_API + "/projects/opalmer/pywincffi"

session = requests.Session()
session.headers.update({
    "Accept": "application/json",
    "Content-Type": "application/json"
})

logger = get_logger("dev.release")


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
        "--recreate", action="store_true", default=False,
        help="If provided, recreate the release"
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    version = ".".join(map(str, __version__))

    # Make sure we really want to create a release of this version.
    should_continue(
        "Create release of version %s? [y/n] " % version,
        skip=args.confirm
    )

    if not args.skip_github:
        github = GitHubAPI(version)

        if github.milestone.state != "closed":
            should_continue(
                "GitHub milestone %s is still open, continue? [y/n]" % version,
                skip=args.confirm)

        release = github.create_release(
            recreate=args.recreate, dry_run=args.dry_run,
            close_milestone=not args.keep_milestone_open)

        # TODO: Hack around in PyGitHub's request context so we can
        # upload release artifacts
        logger.warning("You must manually upload release artifacts")

        logger.info("Created GitHub release")

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
