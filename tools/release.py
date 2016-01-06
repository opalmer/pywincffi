#!/usr/bin/env python

from __future__ import with_statement

import argparse
import os
import sys
import subprocess
import tempfile
import shutil
from os.path import dirname, abspath, isdir, basename, join

import requests

# Add the root of the repo to sys.path so
# we can import pywcinffi directly.
sys.path.insert(0, dirname(dirname(abspath(__file__))))

from pywincffi import __version__

APPVEYOR_API = "https://ci.appveyor.com/api"
APPVEYOR_API_PROJ = APPVEYOR_API + "/projects/opalmer/pywincffi"

session = requests.Session()
session.headers.update({
    "Accept": "application/json",
    "Content-Type": "application/json"
})


def should_continue(question, questions=True):
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


def get_release_artifacts(args, data):
    paths = []

    # Locate the build artifacts and download them
    print("Downloading build artifacts to %s" % args.artifacts)
    for job in data["build"]["jobs"]:
        job_id = job["jobId"]
        if job["status"] != "success":
            print("... status of job %s != success" % job_id)
            raise Exception("Cannot publish a failed job.")

        # Iterate over and download all the artifacts
        artifact_url = APPVEYOR_API + "/buildjobs/%s/artifacts" % job_id
        build_artifacts = session.get(artifact_url).json()
        if not build_artifacts:
            raise Exception("Build %s does not contain any artifacts" % url)

        for artifact in build_artifacts:
            if artifact["type"] != "File" or not \
                 artifact["fileName"].endswith(".whl"):
                continue

            file_url = artifact_url + "/%s" % artifact["fileName"]
            print("... download and unpack %s" % artifact["fileName"])
            local_path = join(args.artifacts, basename(artifact["fileName"]))
            response = session.get(
                file_url, stream=True, headers={"Content-Type": ""})

            with open(local_path, "wb") as file_:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file_.write(chunk)

            # Unpack the wheel to be sure the structure is correct.  This
            # helps to ensure that the download not incomplete or corrupt.
            unpack_dir = tempfile.mkdtemp()
            try:
                subprocess.check_call([
                    "wheel", "unpack", file_.name, "--dest", unpack_dir],
                    stderr=subprocess.PIPE)
            except subprocess.CalledProcessError:
                raise Exception("Failed to unpack %s" % file_.name)
            finally:
                shutil.rmtree(unpack_dir, ignore_errors=True)

    return paths



def main(questions=True):
    parser = argparse.ArgumentParser(description="Cuts a release of pywincffi")
    parser.add_argument(
        "--no-publish", action="store_true", default=False,
        help="If provided, do everything publish is supposed to do...minus the "
             "publish part."
    )
    parser.add_argument(
        "--artifact-directory", default=tempfile.mkdtemp(), dest="artifacts",
        help="The temp. location to download build artifacts to."
    )
    args = parser.parse_args()

    if not isdir(args.artifacts):
        os.makedirs(args.artifacts)

    version = ".".join(map(str, __version__))

    # Make sure we really want to create a release of this version.
    should_continue(
        "Create release of version %s? [y/n] " % version, questions=questions)

    # Find the last passing build on the master branch.
    url = APPVEYOR_API_PROJ + "/branch/master"
    data = session.get(url).json()
    build_message = data["build"]["message"]

    should_continue(
        "Create release from %r? [y/n] " % build_message, questions=questions)
    paths = get_release_artifacts(args, data)


if __name__ == "__main__":
    # TODO: remove `questions=False`
    main(questions=False)
