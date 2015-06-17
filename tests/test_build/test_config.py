from __future__ import print_function

import os
import tempfile
try:
    from unittest import TestCase, skipIf
except ImportError:
    from unittest2 import TestCase, skipIf

get_config = None
try:
    from pywincffi.build.config import (
        DEFAULT_CONFIG_PACKAGE, DEFAULT_CONFIG_USER, get_config)
except ImportError:
    pass
else:
    from configparser import ConfigParser

from os.path import isfile

@skipIf(get_config is None, "pywincffi.build.config was not be imported")
class TestConfig(TestCase):
    def test_instance(self):
        config = get_config()
        self.assertIsInstance(config, ConfigParser)

    def test_package_config_exists(self):
        # The package configuration should exist.  If not, then there's
        # probably something wrong with the setup.py
        self.assertTrue(isfile(DEFAULT_CONFIG_PACKAGE))

    def test_default_sections(self):
        # If we read in the config using the DEFAULT_* constants
        # and using get_config we should retrieve the same sections.
        config = ConfigParser()
        config.read([
            DEFAULT_CONFIG_PACKAGE,
            DEFAULT_CONFIG_USER
        ])
        package_config = get_config()
        self.assertEqual(config.sections(), package_config.sections())

    def test_reads_additional_files_string(self):
        # get_config() accepts a string (converted to list)
        fd, path = tempfile.mkstemp()
        self.addCleanup(os.remove, path)

        with os.fdopen(fd, "w") as tmpfile:
            print("[foo]", file=tmpfile)
            print("bar = 1", file=tmpfile)

        config = get_config(files=path)
        self.assertEqual(config.getint("foo", "bar"), 1)

    def test_reads_additional_files_list(self):
        # get_config() accepts a list
        fd, path = tempfile.mkstemp()
        self.addCleanup(os.remove, path)

        with os.fdopen(fd, "w") as tmpfile:
            print("[foo]", file=tmpfile)
            print("bar = 1", file=tmpfile)

        config = get_config(files=[path])
        self.assertEqual(config.getint("foo", "bar"), 1)
