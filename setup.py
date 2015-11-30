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

py_major, py_minor = sys.version_info[0:2]

if py_major == 2:
    tests_require.append("unittest2")

if py_major == 2 and py_minor == 6:
    # Later versions don't work with 2.6
    tests_require.append("mock==1.0.1")

else:
    try:
        from unittest import mock
    except ImportError:
        tests_require.append("mock")

try:
    import enum
except ImportError:
    install_requires_extras.append("enum34")

setup(
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
