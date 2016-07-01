import logging

from pywincffi.core.logger import (
    STREAM_HANDLER, FORMATTER, logger, get_logger)
from pywincffi.dev.testutil import TestCase


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
    def setUp(self):
        super(TestGetLogger, self).setUp()
        self.logger_name = self.random_string(10)
        self.logger = get_logger(self.logger_name)
        self.addCleanup(self.logger.manager.loggerDict.pop, self.logger.name)

    def test_return_type(self):
        self.assertIsInstance(get_logger(self.logger_name), logging.Logger)

    def test_disallows_name_starting_with_dot(self):
        with self.assertRaises(ValueError):
            get_logger(".%s" % self.logger_name)

    def test_child_logger_name(self):
        self.assertEqual(
            self.logger.name, ".".join([logger.name, self.logger_name]))

    def test_child_logger_has_no_handlers(self):
        child = get_logger(self.logger_name)
        self.assertEqual(child.handlers, [])

    def test_child_logger_propagation(self):
        child = get_logger(self.logger_name)
        self.assertEqual(child.propagate, 1)
