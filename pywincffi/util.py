"""
Utility
=======

High level utilities used for converting types and working
with Python and CFFI.  These are not part of :mod:`pywincffi.core`
because they're not considered an internal implementation feature.
"""

from six import PY2, PY3

from pywincffi.core import dist


def string_to_cdata(string, unicode_cast=True):
    """
    Converts ``string`` to an equivalent cdata type depending
    on the Python version, initial type of ``string`` and the
    ``unicode_cast`` flag.  This function is mostly meant to
    be used internally by pywincffi but could be used
    elsewhere too.

    :type string: str, unicode
    :param string:
        The string to convert to a cdata object.

    :keyword bool unicode_cast:
        If True (the default) and running Python 2 ``string`` will be
        converted to unicode prior to being processed.

        This defaults to True because pywincffi calls
        :meth:`cffi.FFI.set_unicode` which causes types like TCHAR and
        LPTCSTR to point to wchar_t.  In Python 3, strings are unicode by
        default so this extra conversion step is not necessary.  In
        Python 2 the conversion is necessary because you end up
        subtle problems inside of the Windows APIs as a result

    :raises TypeError:
        Raised if the function can't determine how to convert
    """
    ffi, _ = dist.load()

    if PY2 and isinstance(string, str) and unicode_cast:
        string = unicode(string)  # pylint: disable=undefined-variable

    # Convert to wchar_t if ``string`` is unicode.
    # pylint: disable=undefined-variable
    if PY3 and isinstance(string, str) or PY2 and isinstance(string, unicode):
        return ffi.new("wchar_t[]", string)

    # Convert to char[] if ``string`` is a regular string.  This
    # is only for Python 2 and nly if ``force_unicode`` is False.
    elif PY2 and isinstance(string, str):
        return ffi.new("char[]", string)

    else:
        raise TypeError(
            "Failed to determine how to convert the provided input, "
            "%r (type: %s), to a cdata object" % (string, type(string)))
