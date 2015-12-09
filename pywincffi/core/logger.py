"""
Logger
------

This module contains pywincffi's logger and provides functions to
configure the logger at runtime.
"""

import logging

from pywincffi.core.config import config

try:
    NullHandler = logging.NullHandler

except AttributeError:  # pragma: no cover
    # Python 2.6 does not have a NullHandler
    class NullHandler(logging.Handler):
        """
        A Python 2.6 implementation of Python 2.7's
        :class:`logging.NullHandler`
        """
        def handle(self, record):
            pass

        def emit(self, record):
            pass

        def createLock(self):
            self.lock = None

FORMATTER = logging.Formatter(
    "%(asctime)s %(name)s %(levelname)9s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S")
STREAM_HANDLER = logging.StreamHandler()
STREAM_HANDLER.setFormatter(FORMATTER)
NULL_HANDLER = NullHandler()

logger = logging.getLogger("pywincffi")
logger.addHandler(NULL_HANDLER)


def get_logger(name):
    """
    Returns an instance of :class:`logging.Logger` as a child of
    pywincffi's main logger.

    :param str name:
        The name of the child logger to return. For example,
        if you provide `foo` for the name the resulting name
        will be `pywincffi.foo`.

    :raises ValueError:
        Raised if ``name`` starts with a dot.

    :rtype: :class:`logging.Logger`
    """
    if name.startswith("."):
        raise ValueError("`name` cannot start with '.'")

    try:
        child_logger = logger.getChild(name)

    # getChild was introduced in Python 2.6
    except AttributeError:
        child_logger = logging.getLogger(logger.name + "." + name)

    configured_level = config.logging_level()

    # Root logging configuration has changed, reconfigure.
    if logger.level != configured_level:
        if configured_level == logging.NOTSET:
            logger.handlers[:] = [NULL_HANDLER]
        else:
            logger.handlers[:] = [STREAM_HANDLER]

        logger.setLevel(configured_level)

    return child_logger
