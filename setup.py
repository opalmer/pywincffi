from __future__ import print_function

import os
import sys
from errno import ENOENT
from os.path import dirname, abspath, join, isdir

from setuptools import setup, find_packages
from distutils.command.upload import upload

from pywincffi import __version__


try:
    WindowsError
except NameError:
    WindowsError = OSError

try:
    with open("README.rst") as readme:
        long_description = readme.read()
except (OSError, IOError, WindowsError) as error:
    if error.errno == ENOENT:
        long_description = ""
    else:
        raise

requirements = [
    "cffi>=1.6.0",
    "six"
]

if sys.version_info[0:2] < (3, 4):
    requirements += ["enum34"]

ROOT = dirname(abspath(__file__))
DISTS = join(ROOT, "dist")


class AppVeyorArtifactUpload(upload):
    """
    A subclass of the normal upload command which
    """
    def run(self):
        if not isdir(DISTS):
            print("%s does not exist" % DISTS, file=sys.stderr)
            sys.exit(1)

        # Clean out everything in dist/* first.  This ensures that
        # if we have local files they'll be replaced by the artifacts
        # that we're downloading.
        for root, dirs, files in os.walk(DISTS):
            for name in files:
                os.remove(join(root, name))

        from pywincffi.dev.release import AppVeyor
        appveyor = AppVeyor()

        for artifact in appveyor.artifacts(directory=DISTS):
            extension = artifact.path.split(".")[-1]
            if extension not in ("whl", "zip", "msi", "exe"):
                continue

        for root, dirs, files in os.walk(DISTS):
            for filename in files:
                if filename.endswith(".zip"):
                    command = "sdist"
                    pyversion = "none"
                elif filename.endswith(".whl"):
                    command = "bdist_wheel"
                    _, _, pyversion, _, _ = filename.rstrip(".whl").split("-")
                    pyversion = ".".join(list(pyversion.lstrip("cp")))
                elif filename.endswith(".msi"):
                    command = "bdist_msi"
                    pyversion = \
                        filename.rstrip(".msi").split("-")[-1].lstrip("py")
                elif filename.endswith(".exe"):
                    command = "bdist_wininst"
                    raise NotImplementedError(
                        "Don't have `pyversion` implemented for %r" % filename)
                else:
                    print(
                        "Unknown file type: %r" % filename.split(".")[-1],
                        file=sys.stderr)
                    sys.exit(1)

                filename = join(root, filename)
                self.upload_file(command, pyversion, filename)

setup_keywords = dict(
    name="pywincffi",
    version=".".join(map(str, __version__)),
    cmdclass={
      "upload_from_appveyor": AppVeyorArtifactUpload
    },
    packages=find_packages(
        include=("pywincffi*", )
    ),
    include_package_data=True,
    author="Oliver Palmer",
    author_email="oliverpalmer@opalmer.com",
    url="http://github.com/opalmer/pywincffi",
    description="A Python library which wraps Windows functions using CFFI",
    long_description=long_description,
    setup_requires=requirements,
    install_requires=requirements,
    test_suite="nose.collector",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Environment :: Win32 (MS Windows)",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries"
    ]
)

# Only add cffi_modules if we're running on Windows.  Otherwise
# things like the documentation build, which can run on Linux, may
# not work.
if os.name == "nt":
    setup_keywords.update(
        cffi_modules=["pywincffi/core/dist.py:_ffi"]
    )

setup(**setup_keywords)
