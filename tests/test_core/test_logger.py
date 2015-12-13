import logging

from mock import patch

from pywincffi.core.config import config
from pywincffi.core.logger import (
    STREAM_HANDLER, FORMATTER, NULL_HANDLER, logger, get_logger)
from pywincffi.core.testutil import TestCase


class TestStreamHandler(TestCase):
    """
    Tests for ``pywincffi.core.logger.STREAM_HANDLER``
    """
    def test_type(self):
        self.assertIsInstance(STREAM_HANDLER, logging.StreamHandler)

    def test_formatter(self):
        self.assertIs(STREAM_HANDLER.formatter, FORMATTER)


class TestDefaultLogger(TestCase):
    """
    Tests for ``pywincffi.core.logger.logger``
    """
    def test_type(self):
        self.assertIsInstance(logger, logging.Logger)

    def test_name(self):
        self.assertEqual(logger.name, "pywincffi")


class TestGetLogger(TestCase):
    """
    Tests for ``pywincffi.core.logger.get_logger``
    """
    count = 0

    def setUp(self):
        super(TestGetLogger, self).setUp()
        self.level = logger.level
        self.handlers = logger.handlers[:]
        self.count += 1

    def tearDown(self):
        super(TestGetLogger, self).tearDown()
        logger.level = self.level
        logger.handlers[:] = self.handlers

    def test_return_type(self):
        self.assertIsInstance(
            get_logger("foo.%s" % self.count), logging.Logger)

    def test_disallows_name_starting_with_dot(self):
        with self.assertRaises(ValueError):
            get_logger(".foo.%s" % self.count)

    def test_child_logger_name(self):
        child = get_logger("foo.%s" % self.count)
        self.assertEqual(child.name, logger.name + "." + "foo.%s" % self.count)

    def test_child_logger_has_no_handlers(self):
        child = get_logger("foo.%s" % self.count)
        self.assertEqual(child.handlers, [])

    def test_child_logger_propagation(self):
        child = get_logger("foo.%s" % self.count)
        self.assertEqual(child.propagate, 1)

    def test_get_logger_configures_level(self):
        logger.level = False
        get_logger("foo.%s" % self.count)
        self.assertEqual(config.logging_level(), logger.level)

    def test_level_not_set(self):
        logger.handlers.append(True)
        logger.level = logging.DEBUG

        with patch.object(config,
                          "logging_level", return_value=logging.NOTSET):
            get_logger("foo.%s" % self.count)

        self.assertEqual(logger.level, logging.NOTSET)
        self.assertEqual(logger.handlers, [NULL_HANDLER])

    def test_other_level(self):
        logger.level = logging.NOTSET
        logger.handlers.append(True)

        with patch.object(config,
                          "logging_level", return_value=logging.CRITICAL):
            get_logger("foo.%s" % self.count)

        self.assertEqual(logger.level, logging.CRITICAL)
        self.assertEqual(logger.handlers, [STREAM_HANDLER])
