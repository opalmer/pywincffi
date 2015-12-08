"""
Logger
------

This module contains pywincffi's logger and provides functions to
configure the logger at runtime.
"""

import logging
import sys

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

UNSET = object()

logger = logging.getLogger("pywincffi")
logger.addHandler(NullHandler())


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
            logger.handles[:] = []  # pylint: disable=no-member
            logger.setLevel(configured_level)
            logger.addHandler(NullHandler())

        else:
            formatter = logging.Formatter(
                "%(asctime)s %(name)s %(levelname)9s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        logger.setLevel(configured_level)

    return child_logger


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
