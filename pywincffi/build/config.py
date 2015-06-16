"""
Config
======

Handles the configuration object for :mod:`pywincffi.build`.
"""

from os.path import join, expanduser

import six
from pkg_resources import resource_filename
from configparser import ConfigParser

DEFAULT_CONFIG_PACKAGE = resource_filename("pywincffi", "build/.pywincffi")
DEFAULT_CONFIG_USER = join(expanduser("~"), ".pywincffi")

def get_config(files=None):
    """
    Returns an instance of :class:`SafeConfigParser` using ``files``
    as input.

    :param list files:
        Optional list of files to read the configuration from.  If this
        value is not provided we'll read from ``build/.pywincffi`` and
        ``~/.pywincffi``.

    .. note::

        This function does not cache the results.  Calling this function
        will reload the config completely (which is useful for long running
        processes).
    """
    config_files = [DEFAULT_CONFIG_PACKAGE, DEFAULT_CONFIG_USER]
    if isinstance(files, six.string_types):
        files = [files]

    if isinstance(files, list):
        config_files.extend(files)

    config = ConfigParser()
    config.read(config_files)
    return config
