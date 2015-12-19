import os
import sys
from errno import ENOENT
from setuptools import setup, find_packages

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

base_requirements = [
    "cffi>=1.0.0",
    "six",
    "wheel>=0.26.0",
    "setuptools>=18.0"
]

install_requirements = base_requirements[:]
setup_requirements = base_requirements[:]
test_requirements = base_requirements[:]

if sys.version_info[0] == 2:
    test_requirements += ["unittest2"]
    install_requirements += ["enum34"]

if sys.version_info[0:2] == (2, 6):
    test_requirements += ["mock==1.0.1"]
else:
    test_requirements += ["mock"]

if os.environ.get("READTHEDOCS"):
    install_requirements += ["sphinx"]

test_requirements += ["nose", "coverage"]


setup_keywords = dict(
    name="pywincffi",
    version="0.1.0",
    packages=find_packages(
        include=("pywincffi*", )
    ),
    include_package_data=True,
    author="Oliver Palmer",
    description="A Python library which wraps Windows functions using CFFI",
    long_description=long_description,
    setup_requires=setup_requirements,
    install_requires=install_requirements,
    tests_require=test_requirements,
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
