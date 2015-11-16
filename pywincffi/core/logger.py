"""
Logger
------

This module contains pywincffi's logger and provides functions to
configure the logger at runtime.
"""

import logging
import sys

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

UNSET = object()

logger = logging.getLogger("pywincffi")
logger.addHandler(NullHandler())


def get_logger(name):
    """Returns a child of the parent logger for pywincffi"""
    if name.startswith("."):
        raise ValueError("`name` cannot start with '.'")

    if sys.version_info[0:2] <= (2, 6):
        return logging.getLogger(logger.name + "." + name)

    return logger.getChild(name)


def configure(level, handler=None, formatter=None):
    """
    Enables pywincffi's logger, adds formatting, handling and sets
    the logging level.  Normally pywincffi's logger is not configured
    and logs nothing, this function will enable it however and can
    be useful for debugging.

    :param int level:
        The level to apply to the logger.  The ``pywincffi.core.loggger.UNSET``
        global can also be used here to revert the logger back to its original
        state.

    :keyword logging.Handler handler:
        An instance of a handler to add to the logger.  If none is provided
        then :class:`logging.StreamHandler` will be used instead.

    :keyword logging.Formatter formatter:
        The formatter to apply to the logger. If none is provided
        then ``%(asctime)s %(name)s %(levelname)9s %(message)s"`` will
        be used as the format.
    """
    if formatter is None:
        formatter = logging.Formatter(
            "%(asctime)s %(name)s %(levelname)9s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    if handler is None:
        handler = logging.StreamHandler()

    if level is UNSET:
        logger.handlers[:] = []
        logger.setLevel(logging.CRITICAL)
        logger.addHandler(NullHandler())
    else:
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
