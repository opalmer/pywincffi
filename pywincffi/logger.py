"""
Logger
======

This module contains pywincffi's logger and provides functions to
configure the logger at runtime.
"""

import logging

try:
    NullHandler = logging.NullHandler

except AttributeError:  # Python 2.6
    class NullHandler(logging.Handler):
        def handle(self, record):
            pass

        def emit(self, record):
            pass

        def createLock(self):
            self.lock = None


logger = logging.getLogger("pywincffi")
logger.addHandler(NullHandler())


def configure(level, handler=None, formatter=None):
    """
    Enables pywincffi's logger, add formatting, handling and set
    the logging level.  Normally pywincffi's logger is not configured
    except for an
    """
    if formatter is None:
        formatter = logging.Formatter(
            "%(asctime)s %(name)s %(levelname)9s %(message)s",
            datefmt="%D %H:%M:%S"
        )

    if handler is None:
        handler = logging.StreamHandler()

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
