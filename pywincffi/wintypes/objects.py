"""
Objects
-------

Provides wrappers around core Windows objects such as file handles, sockets,
etc.
"""

# NOTE: This module should *not* import other modules from wintypes.
from pywincffi.core import dist
from pywincffi.core.typesbase import CFFICDataWrapper


# pylint: disable=too-few-public-methods,protected-access
class HANDLE(CFFICDataWrapper):
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
