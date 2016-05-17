"""
Windows Types Package
====================

Provides user accessible types corresponding to the respective Windows types
used across the exposed APIs.
"""


from six import integer_types

from pywincffi.core import typesbase
from pywincffi.core import dist


_ffi, _ = dist.load()


def wintype_to_cdata(wintype):
    """
    :param wintype:
        A type derived from :class:`pywincffi.core.typesbase.CFFICDataWrapper`
    :return:
        The underlying CFFI <cdata> object, or ffi.NULL if wintype is None.
    """
    if wintype is None:
        return _ffi.NULL
    elif isinstance(wintype, HANDLE):
        return wintype._cdata[0]
    else:
        return wintype._cdata


class HANDLE(typesbase.CFFICDataWrapper):
    """
    .. seealso: https://msdn.microsoft.com/en-us/library/aa383751
    """
    def __init__(self, data=None):
        super(HANDLE, self).__init__("HANDLE[1]", _ffi)
        # Initialize from a <cdata handle> object as returned by some
        # Windows API library calls: Python AND FFI types must be equal.
        if isinstance(data, type(self._cdata[0])):
            if _ffi.typeof(data) == _ffi.typeof(self._cdata[0]):
                self._cdata[0] = data

    def __eq__(self, other):
        if not isinstance(other, HANDLE):
            raise TypeError('%r must be a HANDLE' % other)
        return self._cdata[0] == other._cdata[0]


class SECURITY_ATTRIBUTES(typesbase.CFFICDataWrapper):
    """
    .. seealso: https://msdn.microsoft.com/en-us/library/aa379560
    """
    def __init__(self):
        super(SECURITY_ATTRIBUTES, self).__init__(
            "SECURITY_ATTRIBUTES*",
            _ffi,
        )
        self._cdata.nLength = _ffi.sizeof(self._cdata)
        self.lpSecurityDescriptor = _ffi.NULL

    @property
    def nLength(self):
        return self._cdata.nLength

    @nLength.setter
    def nLength(self, _):
        # Can't raise AttributeError.
        # CFFICDataWrapper would fall back to setting self._cdata.nLength .
        raise TypeError('SECURITY_ATTRIBUTES.nLength is read-only')


class OVERLAPPED(typesbase.CFFICDataWrapper):
    """
    .. seealso: https://msdn.microsoft.com/en-us/library/ms684342
    """
    def __init__(self):
        super(OVERLAPPED, self).__init__("OVERLAPPED*", _ffi)


class FILETIME(typesbase.CFFICDataWrapper):
    """
    .. seealso: https://msdn.microsoft.com/en-us/library/ms724284
    """
    def __init__(self):
        super(FILETIME, self).__init__("FILETIME*", _ffi)

