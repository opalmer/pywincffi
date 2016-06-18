"""
Windows Types Package
=====================

Provides user accessible types corresponding to the respective Windows types
used across the exposed APIs.
"""


from pywincffi.core import typesbase
from pywincffi.core import dist


# pylint: disable=protected-access
def wintype_to_cdata(wintype):
    """
    Returns the underlying CFFI cdata object or ffi.NULL if wintype is None.
    Used internally in API wrappers to "convert" pywincffi's Python types to
    the required CFFI cdata objects when calling CFFI functions. Example:

    >>> from pywincffi.core import dist
    >>> from pywincffi.kernel32 import CreateEvent
    >>> from pywincffi.wintypes import wintype_to_cdata
    >>> ffi, lib = dist.load()
    >>> # Get an event HANDLE, using the wrapper: it's a Python HANDLE object.
    >>> hEvent = CreateEvent(False, False)
    >>> # Call ResetEvent directly without going through the wrapper:
    >>> hEvent_cdata = wintype_to_cdata(hEvent)
    >>> result = lib.ResetEvent(hEvent_cdata)

    :param wintype:
        A type derived from :class:`pywincffi.core.typesbase.CFFICDataWrapper`

    :return:
        The underlying CFFI <cdata> object, or ffi.NULL if wintype is None.
    """
    ffi, _ = dist.load()
    if wintype is None:
        return ffi.NULL
    elif isinstance(wintype, HANDLE):
        return wintype._cdata[0]
    else:
        return wintype._cdata


# pylint: disable=too-few-public-methods
class HANDLE(typesbase.CFFICDataWrapper):
    """
    .. seealso::

        https://msdn.microsoft.com/en-us/library/aa383751
    """
    def __init__(self, data=None):
        ffi, _ = dist.load()
        super(HANDLE, self).__init__("HANDLE[1]", ffi)
        # Initialize from a <cdata handle> object as returned by some
        # Windows API library calls: Python AND FFI types must be equal.
        if isinstance(data, type(self._cdata[0])):
            if ffi.typeof(data) == ffi.typeof(self._cdata[0]):
                self._cdata[0] = data

    def __repr__(self):
        ffi, _ = dist.load()
        return "<HANDLE 0x%x at 0x%x>" % (
            int(ffi.cast("intptr_t", self._cdata[0])),
            id(self)
        )

    def __eq__(self, other):
        if not isinstance(other, HANDLE):
            raise TypeError("%r must be a HANDLE" % other)
        return self._cdata[0] == other._cdata[0]


# pylint: disable=invalid-name
class SECURITY_ATTRIBUTES(typesbase.CFFICDataWrapper):
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


# pylint: disable=too-few-public-methods
class OVERLAPPED(typesbase.CFFICDataWrapper):
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
            raise TypeError("%r must be a HANDLE" % handle)
        self._cdata.hEvent = handle._cdata[0]


# pylint: disable=too-few-public-methods
class FILETIME(typesbase.CFFICDataWrapper):
    """
    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms724284
    """
    def __init__(self):
        ffi, _ = dist.load()
        super(FILETIME, self).__init__("FILETIME*", ffi)
