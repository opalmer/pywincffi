"""
Release
=======

A module for developers which can retrieve information for or
produce a release.
"""

import os
import shutil
import subprocess
import tempfile
from errno import EEXIST
from os.path import join, basename

import requests

from pywincffi.core.logger import get_logger

logger = get_logger("dev.release")

APPVEYOR_API = "https://ci.appveyor.com/api"
APPVEYOR_API_PROJ = APPVEYOR_API + "/projects/opalmer/pywincffi"

def _save_response_content(response, path):
    """
    Given a response object from the requests library, iterate over the
    content and save it to ``path``.
    """
    assert isinstance(response, requests.Response)
    with open(path, "wb") as file_:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file_.write(chunk)


def download_build_artifacts(output, jobs):
    """
    Given a build from AppVeyor download the build artifacts
    to the given ``output``.
    """
    assert isinstance(jobs, list)
    try:
        os.makedirs(output)
    except (OSError, IOError) as error:
        if error.errno != EEXIST:
            raise

    paths = []

    # Locate the build artifacts and download them
    logger.debug("Downloading build artifacts to %s", output)
    for job in jobs:
        job_id = job["jobId"]
        if job["status"] != "success":
            print("... status of job %s != success" % job_id)
            raise Exception("Cannot publish a failed job.")

        # Iterate over and download all the artifacts
        artifact_url = APPVEYOR_API + "/buildjobs/%s/artifacts" % job_id
        build_artifacts = requests.get(artifact_url).json()
        if not build_artifacts:
            raise Exception(
                "Build %s does not contain any artifacts" % artifact_url)

        for artifact in build_artifacts:
            if artifact["type"] != "File" or not \
                 artifact["fileName"].endswith(".whl"):
                continue

            file_url = artifact_url + "/%s" % artifact["fileName"]
            logger.info("Download and unpack", file_url)
            local_path = join(output, basename(artifact["fileName"]))
            response = requests.get(
                file_url, stream=True, headers={"Content-Type": ""})

            _save_response_content(response, local_path)
            paths.append(local_path)

            # Unpack the wheel to be sure the structure is correct.  This
            # helps to ensure that the download not incomplete or
            # corrupt.  We don't really care about the resulting files.
            unpack_dir = tempfile.mkdtemp()
            try:
                subprocess.check_call([
                    "wheel", "unpack", local_path, "--dest", unpack_dir],
                    stderr=subprocess.PIPE)
            except subprocess.CalledProcessError:
                raise Exception("Failed to unpack %s" % local_path)
            finally:
                shutil.rmtree(unpack_dir, ignore_errors=True)

    return paths