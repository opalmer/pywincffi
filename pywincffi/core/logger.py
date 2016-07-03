"""
Logger
------

This module contains pywincffi's logger and functions to
retrieve new child loggers.
"""

import logging

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

# By default, pywincffi's logger does nothing
logger = logging.getLogger("pywincffi")
logger.addHandler(NULL_HANDLER)

__all__ = ("logger", "get_logger")


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
        return logger.getChild(name)

    # getChild was introduced in Python 2.6
    except AttributeError:  # pragma: no cover
        return logging.getLogger(logger.name + "." + name)
