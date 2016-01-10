#!/usr/bin/env python

from __future__ import with_statement

import argparse
import logging
import os
import sys
import tempfile
from errno import EEXIST
from os.path import dirname, abspath

try:
    WindowsError
except NameError:
    WindowsError = OSError

import requests

# Add the root of the repo to sys.path so
# we can import pywcinffi directly.
sys.path.insert(0, dirname(dirname(abspath(__file__))))

from pywincffi import __version__
from pywincffi.core.logger import logger as _core_logger
from pywincffi.dev.release import download_build_artifacts, get_appveyor_build

APPVEYOR_API = "https://ci.appveyor.com/api"
APPVEYOR_API_PROJ = APPVEYOR_API + "/projects/opalmer/pywincffi"

session = requests.Session()
session.headers.update({
    "Accept": "application/json",
    "Content-Type": "application/json"
})

_core_logger.setLevel(logging.INFO)


def mkdir(path):
    try:
        os.makedirs(path)
    except (OSError, IOError, WindowsError) as error:
        if error.errno != EEXIST:
            raise RuntimeError("Failed to create %s: %s" % (path, error))


def save_content(response, path):
    """
    Given a response object from the requests library, iterate over the
    content and save it to ``path``.
    """
    assert isinstance(response, requests.Response)
    with open(path, "wb") as file_:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file_.write(chunk)


def should_continue(question, questions=True):
    """
    Asks a question, returns True if the answer is yes.  Calls
    ``sys.exit(1) if not."""
    if not questions:
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
    arguments = parser.parse_args()

    if arguments.artifacts is None:
        arguments.artifacts = tempfile.mkdtemp()
    else:
        mkdir(arguments.artifacts)

    return arguments


def main(questions=True):
    args = parse_arguments()

    version = ".".join(map(str, __version__))

    # Make sure we really want to create a release of this version.
    should_continue(
        "Create release of version %s? [y/n] " % version, questions=questions)

    # Find the last passing build on the master branch.
    data = get_appveyor_build("master")
    build_message = data["build"]["message"]

    should_continue(
        "Create release from %r? [y/n] " % build_message, questions=questions)
    paths = download_build_artifacts(args.artifacts, data["build"]["jobs"])
    print(paths)


if __name__ == "__main__":
    # TODO: remove `questions=False`
    main(questions=False)
