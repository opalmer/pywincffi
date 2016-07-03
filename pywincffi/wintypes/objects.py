"""
Objects
-------

Provides wrappers around core Windows objects such as file handles, sockets,
etc.
"""

# pylint: disable=too-few-public-methods

# NOTE: This module should *not* import other modules from wintypes.
from pywincffi.core import dist
from pywincffi.core.typesbase import CFFICDataWrapper


class WrappedObject(CFFICDataWrapper):
    """
    A wrapper used by other objects in this module to share common
    methods and conversion.
    """
    C_TYPE = None

    def __init__(self, data=None):
        ffi, _ = dist.load()

        if self.C_TYPE is None:
            raise NotImplementedError("`C_TYPE` has not been declared")

        super(WrappedObject, self).__init__(self.C_TYPE, ffi=ffi)

        # Initialize from a <cdata handle> object as returned by some
        # Windows API library calls: Python AND FFI types must be equal.
        if (isinstance(data, ffi.CData) and
                ffi.typeof(data) == ffi.typeof(self._cdata[0])):
            self._cdata[0] = data

    def __repr__(self):
        ffi, _ = dist.load()
        return "<%s 0x%x at 0x%x>" % (
            self.__class__.__name__,
            int(ffi.cast("intptr_t", self._cdata[0])),
            id(self)
        )

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(
                "%r must be a %s object" % (other, self.__class__.__name__))

        # pylint: disable=protected-access
        return self._cdata[0] == other._cdata[0]


class HANDLE(WrappedObject):
    """
    .. seealso::

        https://msdn.microsoft.com/en-us/library/aa383751
    """
    C_TYPE = "HANDLE[1]"


class WSAEVENT(HANDLE):
    """
    Handles interaction with a WSAEVENT object via its cdata.

    .. note::

        This is functionally equivalent to a :class:`HANDLE` object.
    """
    C_TYPE = "WSAEVENT[1]"


class SOCKET(WrappedObject):
    """Handles interaction with a SOCKET object via its cdata"""
    C_TYPE = "SOCKET[1]"
