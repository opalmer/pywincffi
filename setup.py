import os
import sys
from errno import ENOENT

from setuptools import setup, find_packages

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
    "cffi>=1.0.0",
    "six"
]

if sys.version_info[0:2] < (3, 4):
    requirements += ["enum34"]

setup_keywords = dict(
    name="pywincffi",
    version=".".join(map(str, __version__)),
    packages=find_packages(
        include=("pywincffi*", )
    ),
    include_package_data=True,
    author="Oliver Palmer",
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
        cffi_modules=["pywincffi/core/dist.py:ffi"]
    )

setup(**setup_keywords)
