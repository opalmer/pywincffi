"""
Configuration
=============

Simple module for loading pywincffi's configuration, intended
for internal use. A configuration file which is reasonable for
every day use ships with pywincffi but can be overridden at
runtime by  dropping a file named ``pywincffi.ini`` in the
current working directory or the current users's home directory.
"""

import logging
from os.path import join, expanduser

try:
    from configparser import RawConfigParser
except ImportError:
    from ConfigParser import RawConfigParser

from pkg_resources import resource_filename

from pywincffi.exceptions import ConfigurationError


class Configuration(object):
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

    def __init__(self):
        self.parser = RawConfigParser()
        self.parser.read(self.FILES)

    def precompiled(self):
        """
        Returns True if the configuration states that we should be using
        the precompiled library rather than trying to compile inline.
        """
        return self.parser.get("pywincffi", "library") == "precompiled"

    def logging_level(self):
        """
        Returns the logging level that the configuration currently
        dictates.
        """
        level = self.parser.getint("pywincffi", "log_level")
        if level not in logging._levelToName:
            raise ConfigurationError(
                "Invalid level %s, valid levels are %s" % (
                    level, " ".join(logging._levelToName.keys())))
        return level

config = Configuration()
