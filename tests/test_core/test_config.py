from __future__ import print_function

import logging
import os
from textwrap import dedent
from os.path import isfile, join, expanduser

from mock import patch
from six import PY3

from pywincffi.core.config import Configuration
from pywincffi.dev.testutil import TestCase
from pywincffi.exceptions import ConfigurationError


class TestFiles(TestCase):
    """
    Tests for ``pywincffi.core.config.Configuration.FILES``
    """
    def test_files_type(self):
        self.assertIsInstance(Configuration.FILES, tuple)

    def test_base_file_exists(self):
        self.assertTrue(isfile(Configuration.FILES[0]))


class TestLoggerLevelMappings(TestCase):
    """
    Tests for ``pywincffi.core.config.Configuration.LOGGER_LEVEL_MAPPINGS``
    """
    def levels(self):
        try:
            levels = logging._levelToName  # pylint: disable=no-member
        except AttributeError:
            levels = logging._levelNames  # pylint: disable=no-member

        for key, value in levels.items():
            if isinstance(key, int):
                yield value.lower(), key

    def test_mappings_type(self):
        self.assertIsInstance(Configuration.LOGGER_LEVEL_MAPPINGS, dict)

    def test_lower_case_in_level_mappings(self):
        for key in Configuration.LOGGER_LEVEL_MAPPINGS:
            self.assertTrue(key.islower())

    def test_mapping_levels(self):
        mappings = Configuration.LOGGER_LEVEL_MAPPINGS.copy()
        known_keys = []

        for key, _ in self.levels():
            known_keys.append(key)
            self.assertIn(key, mappings)
            mappings.pop(key)

        # There should not be any extra mappings
        # remaining.
        self.assertEqual(mappings, {})


class TestLoad(TestCase):
    """
    Tests for ``pywincffi.core.config.Configuration.load``
    """
    def write_config(self, path, log_level):
        with open(path, "w") as config:
            print("[pywincffi]", file=config)
            print("library=precompiled", file=config)
            print("log_level=%s" % log_level, file=config)
        self.addCleanup(os.remove, path)

    def test_clear_only_exists_on_py3(self):
        config = Configuration()
        hasattr_ = hasattr(config, "clear")

        if PY3:
            self.assertTrue(hasattr_)
        else:
            self.assertFalse(hasattr_)

    def test_read_loads_files(self):
        with patch.object(Configuration, "read") as mocked:
            Configuration()

        mocked.assert_called_once_with(Configuration.FILES)

    def test_default_log_level(self):
        with patch.object(Configuration, "FILES", (Configuration.FILES[0], )):
            config = Configuration()
            self.assertEqual(config.logging_level(), logging.WARNING)

    def test_contains_override_path_home(self):
        path = join(expanduser("~"), "pywincffi.ini")
        self.assertIn(path, Configuration.FILES)

    def test_contains_override_path_local(self):
        path = "pywincffi.ini"
        self.assertIn(path, Configuration.FILES)

    def test_loads_override(self):
        paths = (
            Configuration.FILES[0],
            self.tempfile(data=dedent("""
            [pywincffi]
            log_level=-1
            """))
        )
        with patch.object(Configuration, "FILES", paths):
            config = Configuration()
            self.assertEqual(config.getint("pywincffi", "log_level"), -1)


class TestLoggingLevel(TestCase):
    """
    Tests for ``pywincffi.core.config.Configuration.logging_level``
    """
    def test_unknown_level(self):
        config = Configuration()
        config.set("pywincffi", "log_level", "foobar")

        with self.assertRaises(ConfigurationError):
            config.logging_level()

    def test_mappings(self):
        for key, value in Configuration.LOGGER_LEVEL_MAPPINGS.items():
            config = Configuration()
            config.set("pywincffi", "log_level", key)
            self.assertEqual(config.logging_level(), value)
