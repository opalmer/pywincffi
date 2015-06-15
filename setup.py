import os
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

exclude = ("pywincffi.build*", )
if "PYWINCFFI_INSTALL_BUILD" in os.environ:
    exclude = ()
    install_requires_extras += ["boto"]

setup(
    name="pywincffi",
    version="0.1.0",
    packages=find_packages(
        include=("pywincffi*", ),
        exclude=exclude
    ),
    author="Oliver Palmer",
    description="A Python library which wraps Windows functions using CFFI",
    long_description=long_description,
    install_requires=[
        "cffi>=1.1.0",
        "six"
    ] + install_requires_extras,
    tests_require=[
        "nose"
    ],
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
