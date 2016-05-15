"""
Windows Types Package
====================

Provides user accessible types corresponding to the respective Windows types
used across the exposed APIs.
"""


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
    return _ffi.NULL if wintype is None else wintype._cdata


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

