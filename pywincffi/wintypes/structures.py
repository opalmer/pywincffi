"""
Structures
----------

This module provides wrappers for structures produced or required by the
Windows APIs.
"""

from pywincffi.core import dist
from pywincffi.core.typesbase import CFFICDataWrapper
from pywincffi.wintypes.objects import HANDLE


# pylint: disable=too-few-public-methods,invalid-name
class SECURITY_ATTRIBUTES(CFFICDataWrapper):
    """
    .. seealso::

        https://msdn.microsoft.com/en-us/library/aa379560
    """
    def __init__(self):
        ffi, _ = dist.load()
        super(SECURITY_ATTRIBUTES, self).__init__(
            "SECURITY_ATTRIBUTES*",
            ffi,
        )
        self._cdata.nLength = ffi.sizeof(self._cdata)
        self.lpSecurityDescriptor = ffi.NULL

    # pylint: disable=missing-docstring
    @property
    def nLength(self):
        return self._cdata.nLength

    # pylint: disable=missing-docstring,no-self-use
    @nLength.setter
    def nLength(self, _):
        # Can't raise AttributeError.
        # CFFICDataWrapper would fall back to setting self._cdata.nLength .
        raise TypeError("SECURITY_ATTRIBUTES.nLength is read-only")


# pylint: disable=too-few-public-methods,protected-access
class OVERLAPPED(CFFICDataWrapper):
    """
    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms684342
    """
    def __init__(self):
        ffi, _ = dist.load()
        super(OVERLAPPED, self).__init__("OVERLAPPED*", ffi)

    # pylint: disable=missing-docstring
    @property
    def hEvent(self):
        return HANDLE(self._cdata.hEvent)

    # pylint: disable=missing-docstring
    @hEvent.setter
    def hEvent(self, handle):
        if not isinstance(handle, HANDLE):
            raise TypeError("%r must be a HANDLE object" % handle)
        self._cdata.hEvent = handle._cdata[0]


# pylint: disable=too-few-public-methods
class FILETIME(CFFICDataWrapper):
    """
    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms724284
    """
    def __init__(self):
        ffi, _ = dist.load()
        super(FILETIME, self).__init__("FILETIME*", ffi)


class LPWSANETWORKEVENTS(CFFICDataWrapper):
    """
    .. seealso::

         https://msdn.microsoft.com/en-us/ms741653
    """
    def __init__(self):
        ffi, _ = dist.load()
        super(LPWSANETWORKEVENTS, self).__init__("LPWSANETWORKEVENTS", ffi)

    @property
    def iErrorCode(self):
        """An array of integers containing any associated error codes"""
        return tuple(self._cdata.iErrorCode)
