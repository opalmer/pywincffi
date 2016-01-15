#!/usr/bin/env python

from __future__ import with_statement

import argparse
import sys
from os.path import dirname, abspath

try:
    WindowsError
except NameError:  # pragma: no cover
    WindowsError = OSError

import requests

# Add the root of the repo to sys.path so
# we can import pywcinffi directly.
sys.path.insert(0, dirname(dirname(abspath(__file__))))

from pywincffi import __version__
from pywincffi.core.logger import get_logger
from pywincffi.dev.release import AppVeyor, GitHubAPI

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
        "--no-publish", action="store_true", default=False,
        help="If provided, do everything publish is supposed to do...minus the "
             "publish part."
    )
    parser.add_argument(
        "--artifact-directory", default=None, dest="artifacts",
        help="The temp. location to download build artifacts to."
    )
    parser.add_argument(
        "--retag", default=False, action="store_true",
        help="If provided, overwrite the previous tag"
    )
    return parser.parse_args()


def main(ask_questions=True):
    args = parse_arguments()

    version = ".".join(map(str, __version__))

    # Make sure we really want to create a release of this version.
    should_continue(
        "Create release of version %s? [y/n] " % version,
        skip=not ask_questions
    )

    # Find the last passing build on the master branch.
    appveyor = AppVeyor()
    should_continue(
        "Create release from %r? [y/n] " % appveyor.message,
        skip=not ask_questions
    )

    for artifact in appveyor.artifacts(directory=args.artifacts):
        extension = artifact.path.split(".")[-1]
        if extension not in ("whl", "zip", "msi", "exe"):
            continue

    github = GitHubAPI()

if __name__ == "__main__":
    # TODO: remove `questions=False`
    main(ask_questions=False)
