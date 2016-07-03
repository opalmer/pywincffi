"""
Ws2_32 Sub-Package
==================

Provides functions, constants and utilities that wrap functions provided by
``ws3_32.dll``.
"""

from pywincffi.ws2_32.events import (
    WSAEventSelect, WSACreateEvent, WSAGetLastError, WSAEnumNetworkEvents)
