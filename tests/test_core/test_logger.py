import logging
import os

from pywincffi.core.logger import HANDLER, NullHandler, logger, get_logger
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


class TestGetLogger(LoggerTestCase):
    def test_invalid_name(self):
        with self.assertRaises(ValueError):
            get_logger(".foo")

    def test_get_child(self):
        expected_name = logger.name + "." + "hello.world"
        child_logger = get_logger("hello.world")
        self.assertEqual(expected_name, child_logger.name)
