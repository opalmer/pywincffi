"""
Windows Types Package
=====================

Provides user accessible types corresponding to the respective Windows types
used across the exposed APIs.
"""

from pywincffi.wintypes.functions import wintype_to_cdata
from pywincffi.wintypes.objects import HANDLE
from pywincffi.wintypes.structures import (
    SECURITY_ATTRIBUTES, OVERLAPPED, FILETIME)
