"""
Windows Types Package
====================

Provides user accessible types corresponding to the respective Windows types
used across the exposed APIs.
"""


from six import integer_types

from pywincffi.core import typesbase
from pywincffi.core import dist


_FFI, _ = dist.load()


# pylint: disable=protected-access
def wintype_to_cdata(wintype):
    """
    :param wintype:
        A type derived from :class:`pywincffi.core.typesbase.CFFICDataWrapper`
    :return:
        The underlying CFFI <cdata> object, or ffi.NULL if wintype is None.
    """
    if wintype is None:
        return _FFI.NULL
    elif isinstance(wintype, HANDLE):
        return wintype._cdata[0]
    else:
        return wintype._cdata


# pylint: disable=too-few-public-methods
class HANDLE(typesbase.CFFICDataWrapper):
    """
    .. seealso: https://msdn.microsoft.com/en-us/library/aa383751
    """
    def __init__(self, data=None):
        super(HANDLE, self).__init__("HANDLE[1]", _FFI)
        # Initialize from a <cdata handle> object as returned by some
        # Windows API library calls: Python AND FFI types must be equal.
        if isinstance(data, type(self._cdata[0])):
            if _FFI.typeof(data) == _FFI.typeof(self._cdata[0]):
                self._cdata[0] = data

    def __repr__(self):
        return "<HANDLE 0x%x at 0x%x>" % (
            int(_FFI.cast("DWORD", self._cdata[0])),
            id(self)
        )

    def __eq__(self, other):
        if not isinstance(other, HANDLE):
            raise TypeError('%r must be a HANDLE' % other)
        return self._cdata[0] == other._cdata[0]


# pylint: disable=invalid-name
class SECURITY_ATTRIBUTES(typesbase.CFFICDataWrapper):
    """
    .. seealso: https://msdn.microsoft.com/en-us/library/aa379560
    """
    def __init__(self):
        super(SECURITY_ATTRIBUTES, self).__init__(
            "SECURITY_ATTRIBUTES*",
            _FFI,
        )
        self._cdata.nLength = _FFI.sizeof(self._cdata)
        self.lpSecurityDescriptor = _FFI.NULL

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


# pylint: disable=too-few-public-methods
class OVERLAPPED(typesbase.CFFICDataWrapper):
    """
    .. seealso: https://msdn.microsoft.com/en-us/library/ms684342
    """
    def __init__(self):
        super(OVERLAPPED, self).__init__("OVERLAPPED*", _FFI)

    # pylint: disable=missing-docstring
    @property
    def hEvent(self):
        return HANDLE(self._cdata.hEvent)

    # pylint: disable=missing-docstring
    @hEvent.setter
    def hEvent(self, handle):
        if not isinstance(handle, HANDLE):
            raise TypeError('%r must be a HANDLE' % handle)
        self._cdata.hEvent = handle._cdata[0]


# pylint: disable=too-few-public-methods
class FILETIME(typesbase.CFFICDataWrapper):
    """
    .. seealso: https://msdn.microsoft.com/en-us/library/ms724284
    """
    def __init__(self):
        super(FILETIME, self).__init__("FILETIME*", _FFI)
