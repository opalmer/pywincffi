import logging
import os

from pywincffi.logger import NullHandler, logger, configure
from pywincffi.testutil import TestCase


class TestLogger(TestCase):
    def setUp(self):
        self.handlers = logger.handlers[:]
        self.level = logger.level

    def tearDown(self):
        logger.handlers[:] = self.handlers
        logger.setLevel(self.level)

    def test_default_handlers(self):
        self.assertEqual(
            [type(handler) for handler in logger.handlers],
            [type(NullHandler())]
        )

    def test_configure_level(self):
        configure(logging.CRITICAL)
        self.assertEqual(logger.level, logging.CRITICAL)

    def test_configure_default_handler(self):
        configure(logging.CRITICAL)
        self.assertEqual(
            [type(handler) for handler in logger.handlers],
            [type(NullHandler()), type(logging.StreamHandler())]
        )

    def test_configure_default_formatter(self):
        configure(logging.CRITICAL)
        handler = logger.handlers[-1]
        self.assertEqual(
            handler.formatter._fmt,
            "%(asctime)s %(name)s %(levelname)9s %(message)s"
        )
        self.assertEqual(
            handler.formatter.datefmt, "%D %H:%M:%S"
        )

    def test_configure_custom_handler(self):
        handler = logging.FileHandler(os.devnull)
        self.addCleanup(handler.close)
        configure(logging.CRITICAL, handler)
        self.assertIs(logger.handlers[-1], handler)

    def test_configure_custom_formatter(self):
        formatter = logging.Formatter(fmt="1234", datefmt="4567")
        configure(logging.CRITICAL, formatter=formatter)
        handler = logger.handlers[-1]
        self.assertEqual(handler.formatter._fmt, "1234")
        self.assertEqual(handler.formatter.datefmt, "4567")
