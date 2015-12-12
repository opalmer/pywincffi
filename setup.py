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

install_requires_extras = []
if "READTHEDOCS" in os.environ:
    install_requires_extras = ["sphinx"]

tests_require = ["nose", "coverage", "setuptools>=17.1"]

if sys.version_info[0:2] == (2, 6):
    # mock - later versions of mock don't work with 2.6
    # unittest2 - backports for new unittest framework features.
    tests_require.extend(["mock==1.0.1", "unittest2"])

else:
    tests_require.append("mock")

try:
    import enum
except ImportError:
    install_requires_extras.append("enum34")


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
    install_requires=[
        "cffi",
        "six"
    ] + install_requires_extras,
    tests_require=tests_require,
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
