"""
Process
-------

Provides functions, constants and utilities that wrap the Windows
functions associated with process management and interaction.  This
module also provides several constants as well, see Microsoft's
documentation for the constant names and their purpose:

    * **Process Security and Access Rights** -
      https://msdn.microsoft.com/en-us/library/windows/desktop/ms684880

.. note::

    Not all constants may be defined
"""

from io import StringIO
from token import STRING
from collections import namedtuple
from tokenize import generate_tokens

from six import integer_types, text_type

from pywincffi.core import dist
from pywincffi.core.checks import Enums, input_check, error_check
from pywincffi.exceptions import (
    WindowsAPIError, PyWinCFFINotImplementedError, InputError)
from pywincffi.kernel32.handle import CloseHandle
from pywincffi.kernel32.synchronization import WaitForSingleObject
from pywincffi.wintypes import (
    HANDLE, SECURITY_ATTRIBUTES, STARTUPINFO, PROCESS_INFORMATION,
    wintype_to_cdata, text_to_wchar)

RESERVED_PIDS = set([0, 4])


def environment_to_string(environment):
    """
    This function is used internally by :func:`CreateProcess` to convert
    the input to ``lpEnvironment`` to a string which the underlying C API
    call will understand.

    >>> from pywincffi.kernel32.process import environment_to_string
    >>> environment_to_string({"A": "a", "B": "b"})
    'A=a\x00B=b'

    :param environment:
        A dictionary or dictionary like object to convert to a string.

    :raises InputError:
        Raised if we cannot convert ``environment`` to a string.  This can
        happen if:

            * ``environment`` is not a dictionary like object.
            * Not all keys and values in the environment are strings (
              str in Python 3.x, unicode in Python 2.x)
            * One or more of the keys contains the `=` symbol.
    """
    try:
        items = environment.iteritems
    except AttributeError:
        try:
            items = environment.items
        except AttributeError:
            raise InputError(
                "environment", environment, None,
                message="Expected a dictionary like object for `environment`")

    converted = []
    for key, value in items():
        if not isinstance(key, text_type):
            raise InputError(
                "environment key %s" % key, type(key),
                expected_types=(text_type, ))

        if not isinstance(value, text_type):
            raise InputError(
                "environment value %s (key: %r)" % (value, key), type(value),
                expected_types=(text_type, ))

        # From Microsoft's documentation on `lpEnvironment`:
        #   Because the equal sign is used as a separator, it must not be used
        #   in the name of an environment variable.
        if "=" in key:
            raise InputError(
                key, key, None,
                message="Environment keys cannot contain the `=` symbol.  "
                        "Offending key: %r" % key)

        converted.append("%s=%s\0" % (key, value))

    return text_type("".join(converted)) + text_type("\0")


def module_name(path):
    """
    Returns the module name for the given ``path``

        >>> module_name(u"C:\\Python27\\python.exe -c 'print True'")
        'C:\\Python27\\python.exe'
        >>> module_name(u"C:\\Program Files (x86)\\Foo\\program.exe -h")
        'C:\\Program'
        >>> module_name(u"'C:\\Program Files (x86)\\Foo\\program.exe' -h")
        'C:\\Program Files (x86)\\Foo\\program.exe'

    This function is used internally by :func:`CreateProcess` to assist in
    validating input to the ``lpCommandLine`` argument.  When calling
    :func:`CreateProcess` if ``lpApplicationName`` is not set then
    ``lpCommandLine``'s module name cannot exceed ``MAX_PATH``.

    :raises TypeError:
        Raised if ``path`` is not a text type.
    """
    # Try to tokenize the input.  In the case of properly quoted strings
    # the module name should be the first entry.
    for type_, string, _, _, line in generate_tokens(StringIO(path).readline):
        if type_ == STRING and line.startswith(string) and line != string:
            module = string
            break
    else:
        module = path.split(" ", 1)[0]

    if not module:
        raise InputError(
            "", None, None,
            message="Failed to determine module name in %r" % path)

    # Make sure we're just getting the module name
    # and not any of the original quote characters.
    quote_characters = ("'", '"')
    if module[0] in quote_characters:
        module = module[1:]

    if module[-1] in quote_characters:
        module = module[:-1]

    return module


def pid_exists(pid, wait=0):
    """
    Returns True if there's a process associated with ``pid``.

    :param int pid:
        The id of the process to check for.

    :keyword int wait:
        An optional keyword that controls how long we tell
        :func:`WaitForSingleObject` to wait on the process.

    :raises ValidationError:
        Raised if there's a problem with the value provided for ``pid``.
    """
    input_check("pid", pid, integer_types)

    # Process IDs which always exist shouldn't need to continue
    # further.
    if pid in RESERVED_PIDS:
        return True

    _, library = dist.load()

    try:
        hProcess = OpenProcess(
            library.PROCESS_QUERY_INFORMATION | library.SYNCHRONIZE,
            False, pid)

    except WindowsAPIError as error:
        # If we can't access the process then it must exist
        # otherwise there would be nothing to access.  We
        # reach this bit of code if the pid in question
        # is owned by another user or the system and
        # the process running this code does not have the
        # rights to query the other process's information.
        if error.errno == library.ERROR_ACCESS_DENIED:
            library.SetLastError(0)
            return True

        # Sometimes the PID we're asking about no longer exists
        # in the stack anywhere so we'll get ERROR_INVALID_PARAMETER
        # so there's not any reason to continue further.
        if error.errno == library.ERROR_INVALID_PARAMETER:
            library.SetLastError(0)
            return False

        raise

    try:
        process_exit_code = GetExitCodeProcess(hProcess)

        # Process may or may not still be running.  If process_exit_code
        # seem to indicate the process is still alive then run one
        # last check to be certain.
        if process_exit_code == library.STILL_ACTIVE:
            wait_result = WaitForSingleObject(hProcess, wait)

            # The process was still running.
            if wait_result == library.WAIT_TIMEOUT:
                return True

            # The process exited while we were waiting
            # on it so it no longer exists.
            elif wait_result == library.WAIT_OBJECT_0:
                return False

            elif wait_result == library.WAIT_ABANDONED:
                raise PyWinCFFINotImplementedError(
                    "An unknown error occurred while running "
                    "pid_exists(%r).  It appears that the call to "
                    "WaitForSingleObject may be been terminated." % pid)

            else:
                raise PyWinCFFINotImplementedError(
                    "Unhandled result from "
                    "WaitForSingleObject(): %r" % wait_result)

        return False

    finally:
        CloseHandle(hProcess)


def GetExitCodeProcess(hProcess):
    """
    Retrieves the exit code of the given process handle.  To retrieve
    a process handle use :func:`OpenProcess`.

    .. warning::

        You may want to use :func:`process_exit_code` instead of this
        function if you're just checking to see if a process has
        exited at all.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms683189

    :param pywincffi.wintypes.HANDLE hProcess:
        The handle of the process to retrieve the exit code for.

    :returns:
        Returns the exit code of the requested process if one
        can be found.
    """
    input_check("hProcess", hProcess, HANDLE)

    ffi, library = dist.load()
    lpExitCode = ffi.new("LPDWORD")
    code = library.GetExitCodeProcess(wintype_to_cdata(hProcess), lpExitCode)
    error_check("GetExitCodeProcess", code=code, expected=Enums.NON_ZERO)
    return lpExitCode[0]


def OpenProcess(dwDesiredAccess, bInheritHandle, dwProcessId):
    """
    Opens an existing local process object.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms684320

    :param int dwDesiredAccess:
        The required access to the process object.

    :param bool bInheritHandle:
        Enables or disable handle inheritance for child processes.

    :param int dwProcessId:
        The id of the local process to be opened.

    :returns:
        Returns a :class:`pywincffi.wintypes.HANDLE` to the opened process.
        This value can be used by other functions such as
        :func:`TerminateProcess`.
    """
    input_check("dwDesiredAccess", dwDesiredAccess, integer_types)
    input_check("bInheritHandle", bInheritHandle, bool)
    input_check("dwProcessId", dwProcessId, integer_types)
    ffi, library = dist.load()

    handle = library.OpenProcess(
        ffi.cast("DWORD", dwDesiredAccess),
        ffi.cast("BOOL", bInheritHandle),
        ffi.cast("DWORD", dwProcessId)
    )
    error_check("OpenProcess")
    return HANDLE(handle)


def GetCurrentProcess():
    """
    Returns a handle to the current thread.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms683179

    .. note::

        Calling :func:`pywincffi.kernel32.handle.CloseHandle` on the handle
        produced by this function will produce an exception.

    :returns:
        The :class:`pywincffi.wintypes.HANDLE` to the current process.
    """
    _, library = dist.load()
    return HANDLE(library.GetCurrentProcess())


def GetProcessId(Process):  # pylint: disable=invalid-name
    """
    Returns the pid of the process handle provided in ``Process``.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms683215

    :param pywincffi.wintypes.HANDLE Process:
        The handle of the process.

    :return:
        Returns an integer which represents the pid of the given
        process handle.
    """
    input_check("Process", Process, HANDLE)
    _, library = dist.load()
    pid = library.GetProcessId(wintype_to_cdata(Process))
    error_check("GetProcessId")
    return pid


def TerminateProcess(hProcess, uExitCode):
    """
    Terminates the specified process and all of its threads.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms686714

    :param pywincffi.wintypes.HANDLE hProcess:
        A handle to the process to be terminated.

    :param int uExitCode:
        The exit code of the processes and threads as a result of calling
        this function.
    """
    input_check("hProcess", hProcess, HANDLE)
    input_check("uExitCode", uExitCode, integer_types)
    ffi, library = dist.load()
    code = library.TerminateProcess(
        wintype_to_cdata(hProcess),
        ffi.cast("UINT", uExitCode)
    )
    error_check("TerminateProcess", code=code, expected=Enums.NON_ZERO)


def CreateToolhelp32Snapshot(dwFlags, th32ProcessID):
    """
    Takes a snapshot of the specified processes, as well as the heaps,
    modules, and threads used by these processes.

    .. seealso::

        https://msdn.microsoft.com/en-us/ms682489

    :param int dwFlags:
        The portions of the system to be included in the snapshot.

    :param int th32ProcessID:
        The process identifier of the process to be included in the snapshot.

    :rtype: :class:`pywincffi.wintypes.HANDLE`

    :return:
        If the function succeeds,
        it returns an open handle to the specified snapshot.
    """
    input_check("dwFlags", dwFlags, integer_types)
    input_check("th32ProcessID", th32ProcessID, integer_types)
    ffi, library = dist.load()
    process_list = library.CreateToolhelp32Snapshot(
        ffi.cast("DWORD", dwFlags),
        ffi.cast("DWORD", th32ProcessID)
    )

    if process_list == library.INVALID_HANDLE_VALUE:  # pragma: no cover
        raise WindowsAPIError(
            "CreateToolhelp32Snapshot", "Invalid Handle",
            library.INVALID_HANDLE_VALUE,
            expected_return_code="not %r" % library.INVALID_HANDLE_VALUE)

    error_check("CreateToolhelp32Snapshot")

    return HANDLE(process_list)


CreateProcessResult = namedtuple(
    "CreateProcessResult",
    ("lpCommandLine", "lpProcessInformation")
)


def CreateProcess(  # pylint: disable=too-many-arguments,too-many-branches
        lpCommandLine, lpApplicationName=None, lpProcessAttributes=None,
        lpThreadAttributes=None, bInheritHandles=True, dwCreationFlags=None,
        lpEnvironment=None, lpCurrentDirectory=None, lpStartupInfo=None):
    """
    Creates a new process and its primary thread.  The process will be
    created in the same security context as the original process.

    .. seealso::

        https://msdn.microsoft.com/en-us/library/ms682425

    :param str lpCommandLine:
        The command line to be executed.  The maximum length of this parameter
        is 32768.  If no value is provided for ``lpApplicationName`` then
        the module name portion of ``lpCommandLine`` cannot exceed
        ``MAX_PATH``.

    :keyword pywincffi.wintypes.STARTUPINFO lpStartupInfo:
        See Microsoft's documentation for additional information.

        .. warning::

            The STARTUPINFOEX structure is not currently supported
            for this input.

    :keyword str lpApplicationName:
        The name of the module or application to be executed.  This can be
        either the fully qualified path name or a partial name.  The system
        path will not be searched.  If no value is provided for this keyword
        then the input to ``lpCommandLine`` will be used by Windows instead.

    :keyword pywincffi.wintypes.SECUREITY_ATTRIBUTES lpProcessAttributes:
        Determines whether the returned handle to the new process object
        can be inherited by child processes.  By default, the handle cannot be
        inherited.

    :keyword pywincffi.wintypes.SECUREITY_ATTRIBUTES lpThreadAttributes:
        Determines if the returned handle to the new thread object can
        be inherited by child processes.  By default, the thread cannot be
        inherited.

    :keyword bool bInheritHandles:
        If True (the default) the handles inherited by the calling process
        are inherited by the new process.

    :keyword int dwCreationFlags:
        Controls the priority class and creation of the process.  By default
        the process will flag will default to
        ``NORMAL_PRIORITY_CLASS | CREATE_UNICODE_ENVIRONMENT``

    :keyword dict lpEnvironment:
        The environment for the new process.  By default the the process
        will be created with the same environment as the parent process.

        .. note::

            All keys and values in the environment must be either unicode
            (Python 2) or strings (Python 3).

    :keyword str lpCurrentDirectory:
        The full path to the current directory for the process.  If not
         provided then the process will have the same working directory
         as the parent process.

    :raises InputError:
        Raised if ``lpCommandLine`` is too long or there are other input
        problems.

    :rtype: :class:`pywincffi.kernel32.process.CreateProcessResult`
    :return:
        Returns a named tuple containing ``lpCommandLine`` and
        ``lpProcessInformation``.  The ``lpProcessInformation`` will
        be an instance of
        :class:`pywincffi.wintypes.structures.PROCESS_INFORMATION`
    """
    ffi, library = dist.load()

    if len(lpCommandLine) > library.MAX_COMMAND_LINE:
        raise InputError(
            "lpCommandLine", lpCommandLine, text_type,
            message="lpCommandLine's length "
                    "cannot exceed %s" % library.MAX_COMMAND_LINE)

    if lpApplicationName is None:
        lpApplicationName = ffi.NULL

        # If lpApplication name is not set then lpCommandLine's
        # module name cannot exceed MAX_PATH.  Rather than letting
        # this hit the Windows API and possibly fail we're check
        # before hand so we can provide a better exception.
        module = module_name(text_type(lpCommandLine))
        if len(module) > library.MAX_PATH:
            raise InputError(
                "lpCommandLine", lpCommandLine, text_type,
                message="lpCommandLine's module name length cannot "
                        "exceed %s if `lpApplicationName` "
                        "is not set. Module name was %r" % (
                            library.MAX_PATH, module))
    else:
        input_check(
            "lpApplicationName", lpApplicationName, allowed_types=(text_type,))

    if lpProcessAttributes is not None:
        input_check(
            "lpProcessAttributes", lpProcessAttributes,
            allowed_types=(SECURITY_ATTRIBUTES, ))
        lpProcessAttributes = wintype_to_cdata(lpProcessAttributes)
    else:
        lpProcessAttributes = ffi.NULL

    if lpThreadAttributes is not None:
        input_check(
            "lpThreadAttributes", lpThreadAttributes,
            allowed_types=(SECURITY_ATTRIBUTES, ))
        lpThreadAttributes = wintype_to_cdata(lpThreadAttributes)
    else:
        lpThreadAttributes = ffi.NULL

    input_check(
        "bInheritHandles", bInheritHandles, allowed_values=(True, False))

    if dwCreationFlags is None:
        dwCreationFlags = \
            library.NORMAL_PRIORITY_CLASS | library.CREATE_UNICODE_ENVIRONMENT

    input_check(
        "dwCreationFlags", dwCreationFlags, allowed_types=(integer_types, ))

    if lpEnvironment is not None:
        lpEnvironment = text_to_wchar(environment_to_string(lpEnvironment))
    else:
        lpEnvironment = ffi.NULL

    if lpCurrentDirectory is not None:
        input_check(
            "lpCurrentDirectory", lpCurrentDirectory,
            allowed_types=(text_type, ))
    else:
        lpCurrentDirectory = ffi.NULL

    if lpStartupInfo is not None:
        # TODO need to add support for STARTUPINFOEX (undocumented)
        input_check(
            "lpStartupInfo", lpStartupInfo, allowed_types=(STARTUPINFO, ))
    else:
        lpStartupInfo = STARTUPINFO()

    lpProcessInformation = PROCESS_INFORMATION()
    code = library.CreateProcess(
        lpApplicationName,
        lpCommandLine,
        lpProcessAttributes,
        lpThreadAttributes,
        bInheritHandles,
        dwCreationFlags,
        lpEnvironment,
        lpCurrentDirectory,
        wintype_to_cdata(lpStartupInfo),
        wintype_to_cdata(lpProcessInformation)
    )
    error_check("CreateProcess", code=code, expected=Enums.NON_ZERO)

    return CreateProcessResult(
        lpCommandLine=lpCommandLine,
        lpProcessInformation=lpProcessInformation)
