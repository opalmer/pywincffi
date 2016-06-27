"""
Types Base
==========

Provides the base types on top of which user visible types will be built.
"""


# pylint: disable=too-few-public-methods
class CFFICDataWrapper(object):
    """
    Base class for exposing Python types and interfaces to pywincffi users:

    * Wraps a CFFI cdata object in self._cdata.
    * Delegates attribute getting/setting to self._cdata, supporting structs.
    * Delegates item getting/setting to self._cdata, supporting arrays.

    Attribute access is not delegated to the wrapped object if the class
    itself contains such an attribute and that attribute is a descriptor; this
    is in place to support @property in sub-classes.

    :param str cdecl:
        C type specification as used in ff.new(cdecl)

    :param cffi.api.FFI ffi:
        FFI instance used to create wrapped cdata object.
    """

    def __init__(self, cdecl, ffi):
        self._cdata = ffi.new(cdecl)

    def __getattr__(self, name):
        return getattr(self._cdata, name)

    def __setattr__(self, name, value):
        # avoid self-recursion setting own attribute: use parent's __setattr__
        if name == "_cdata":
            super(CFFICDataWrapper, self).__setattr__(name, value)
            return

        # support descriptor attributes in child classes
        if hasattr(self.__class__, name):
            try:
                # getattr on class, otherwise descriptor's __get__ is called
                attr = getattr(self.__class__, name)
                # use descriptor protocol to set
                attr.__set__(self, value)
                return
            except AttributeError:
                # attr.__set__ raised this: attr is not a descriptor
                pass

        # fallback case: delegate to self._cdata
        setattr(self._cdata, name, value)

    def __getitem__(self, key):
        return self._cdata.__getitem__(key)

    def __setitem__(self, key, value):
        return self._cdata.__setitem__(key, value)
