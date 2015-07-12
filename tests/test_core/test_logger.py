import logging
import os

from pywincffi.core.logger import (
    UNSET, NullHandler, configure, logger, get_logger)
from pywincffi.core.testutil import TestCase


class LoggerTestCase(TestCase):
    def setUp(self):
        self.handlers = logger.handlers[:]
        self.level = logger.level

    def tearDown(self):
        logger.handlers[:] = self.handlers
        logger.setLevel(self.level)


class TestDefaultHandler(LoggerTestCase):
    def test_default_handlers(self):
        self.assertEqual(
            [type(handler) for handler in logger.handlers],
            [type(NullHandler())]
        )


class TestConfigureLevels(LoggerTestCase):
    def test_level(self):
        configure(logging.CRITICAL)
        self.assertEqual(logger.level, logging.CRITICAL)

    def test_level_unset(self):
        configure(logging.CRITICAL)
        configure(UNSET)
        self.assertEqual(
            [type(handler) for handler in logger.handlers],
            [type(NullHandler())]
        )


class TestConfigureFormatter(LoggerTestCase):
    def test_custom_formatter(self):
        formatter = logging.Formatter(fmt="1234", datefmt="4567")
        configure(logging.CRITICAL, formatter=formatter)
        handler = logger.handlers[-1]
        self.assertEqual(handler.formatter._fmt, "1234")
        self.assertEqual(handler.formatter.datefmt, "4567")

    def test_default_formatter(self):
        configure(logging.CRITICAL)
        handler = logger.handlers[-1]
        self.assertEqual(
            handler.formatter._fmt,
            "%(asctime)s %(name)s %(levelname)9s %(message)s"
        )
        self.assertEqual(
            handler.formatter.datefmt, "%Y-%m-%d %H:%M:%S"
        )


class TestConfigureHandlers(LoggerTestCase):
    def test_default_handler(self):
        configure(logging.CRITICAL)
        self.assertEqual(
            [type(handler) for handler in logger.handlers],
            [type(NullHandler()), type(logging.StreamHandler())]
        )

    def test_custom_handler(self):
        handler = logging.FileHandler(os.devnull)
        self.addCleanup(handler.close)
        configure(logging.CRITICAL, handler)
        self.assertIs(logger.handlers[-1], handler)
