"""
Communications
--------------

A module containing Windows functions related to communications.
"""

from pywincffi.core import dist
from pywincffi.core.checks import Enums, input_check, error_check
from pywincffi.wintypes import HANDLE, wintype_to_cdata


def ClearCommError(hFile):
    """
    Retrieves information about a communications error and reports the
    current status of a communications device.

    .. seealso::

        https://msdn.microsoft.com/en-us/aa363180

    :param pywincffi.wintypes.HANDLE hFile:
        A handle to the communications device, typically created by
        :func:`CreateFile`

    :rtype: tuple
    :return:
        Returns a two element tuple containing the ``lpErrors`` and
        ``lpStat`` result objects.

            * ``lpErrors`` - Contains the mast indicating the type of error
            * ``lpStat`` - A ``COMSTAT`` structure which contains the device's
               information.
    """
    input_check("hFile", hFile, HANDLE)

    ffi, library = dist.load()

    lpErrors = ffi.new("LPDWORD")
    lpStat = ffi.new("LPCOMSTAT")
    code = library.ClearCommError(wintype_to_cdata(hFile), lpErrors, lpStat)
    error_check("ClearCommError", code=code, expected=Enums.NON_ZERO)

    # TODO: Build Python instance of COMSTAT here!
    return lpErrors, lpStat
