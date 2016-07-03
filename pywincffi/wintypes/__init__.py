"""
Windows Types Package
=====================
Provides user accessible types corresponding to the respective Windows types
used across the exposed APIs.
"""

from pywincffi.wintypes.functions import (
    wintype_to_cdata, handle_from_file, socket_from_object)
from pywincffi.wintypes.objects import WrappedObject, HANDLE, WSAEVENT, SOCKET
from pywincffi.wintypes.structures import (
    SECURITY_ATTRIBUTES, OVERLAPPED, FILETIME, LPWSANETWORKEVENTS)
