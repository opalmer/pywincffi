import logging
from os.path import isfile

from pywincffi.core.config import Configuration
from pywincffi.core.testutil import TestCase


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
            levels = logging._levelToName
        except AttributeError:
            levels = logging._levelNames

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

        for key, value in self.levels():
            known_keys.append(key)
            self.assertIn(key, mappings)
            mappings.pop(key)

        # There should not be any extra mappings
        # remaining.
        self.assertEqual(mappings, {})
