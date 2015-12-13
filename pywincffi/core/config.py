"""
Configuration
=============

Simple module for loading pywincffi's configuration, intended
for internal use. A configuration file which is reasonable for
every day use ships with pywincffi but can be overridden at
runtime by dropping a file named ``pywincffi.ini`` in the
current working directory or the current users's home directory.
"""

import logging
import os
import tempfile
from errno import EEXIST
from os.path import join, expanduser

try:
    from configparser import RawConfigParser
except ImportError:
    # pylint: disable=wrong-import-order,import-error
    from ConfigParser import RawConfigParser

from pkg_resources import resource_filename
from six import PY3

from pywincffi.exceptions import ConfigurationError

try:
    WindowsError
except NameError:
    WindowsError = OSError


class Configuration(RawConfigParser):
    """
    Class responsible for loading and retrieving
    data from the configuration files.  This is used
    by a few parts of pywincffi to control various aspects
    of execution.
    """
    # NOTE: This list is documented in the module's documentation.
    FILES = (
        resource_filename("pywincffi", join("core", "pywincffi.ini")),
        expanduser(join("~", "pywincffi.ini")),
        "pywincffi.ini"
    )
    LOGGER_LEVEL_MAPPINGS = {
        "notset": logging.NOTSET,
        "debug": logging.DEBUG,
        "warning": logging.WARNING,
        "info": logging.INFO,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }

    def __init__(self):  # pylint: disable=super-on-old-class
        if PY3:
            super(Configuration, self).__init__()
        else:
            RawConfigParser.__init__(self)

        self.load()

    def load(self):
        """Loads the configuration from disk"""
        try:
            self.clear()
        except AttributeError:
            self.remove_section("pywincffi")

        self.read(self.FILES)

    def precompiled(self):
        """
        Returns True if the configuration states that we should be using
        the precompiled library rather than trying to compile inline.
        """
        return self.get("pywincffi", "library") == "precompiled"

    def logging_level(self):
        """
        Returns the logging level that the configuration currently
        dictates.
        """
        level = self.get("pywincffi", "log_level")

        if level not in self.LOGGER_LEVEL_MAPPINGS:
            raise ConfigurationError(
                "Invalid level %s, valid levels are %s" % (
                    level, " ".join(self.LOGGER_LEVEL_MAPPINGS.keys())))

        return self.LOGGER_LEVEL_MAPPINGS[level]

    def tempdir(self):
        """
        Returns the directory which :class:`cffi.FFI` should use
        to store temporary files.
        """
        entry = self.get("pywincffi", "tempdir")

        try:
            path = entry.format(tempdir=tempfile.gettempdir())
        except KeyError as error:
            raise ConfigurationError(
                "Unknown key %r in pywincffi.tempdir" % error.args[0])

        try:
            os.makedirs(path)
        except (OSError, IOError, WindowsError) as error:
            if error.errno != EEXIST:
                raise

        return path

config = Configuration()  # pylint: disable=invalid-name
