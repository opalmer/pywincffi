Changelog
=========

This document contains information on pywincff's release history.  Later
versions are shown first.


Versions
--------

0.6.0
~~~~~

Notable enhancements and changes are:

    * :issue:`141` - :func:`pywincffi.kernel32.file.ReadFile` has been updated
      to provide improved support for overlapped IO. This is a **breaking change**
      because the return value and signature of the ReadFile function has
      changed.
    * As part of :issue:`141` the following functions have been added:

        * :func:`pywincffi.kernel32.error.GetLastError`
        * :func:`pywincffi.kernel32.error.SetLastError`
        * :func:`pywincffi.kernel32.error.get_error_message`

0.5.0
~~~~~

Notable enhancements and changes are:

    * **Python 2.6 support has been dropped**. Many projects have already moved
      on from Python 2.6 including Twisted which this project was initially
      intended to support. Additionally many libraries or tools that pywincffi
      no longer have direct support for Python 2.6 or simply break in later
      versions. This leads to having to maintain and support older libraries
      in ths build which is going to become increasing difficult. Pull requests
      to support Python 2.6 will be evaluated on a case-by-case basis.
    * Various improvements to the tests and build including replacement of
      nosetests with pytest, transition from pep8 to pycodestyle and upgrading
      tools and libraries to more modern versions.
    * :issue:`123` - Implemented :func:`pywincffi.kernel32.event.SetEvent`
    * :issue:`124` - Implemented :func:`pywincffi.kernel32.file.GetTempPath`
    * :issue:`129` - Implemented :func:`pywincffi.kernel32.console.SetConsoleTextAttribute`. Also
      implemented :func:`pywincffi.kernel32.console.GetConsoleScreenBufferInfo` and
      :func:`pywincffi.kernel32.console.CreateConsoleScreenBuffer` to properly test
      the new functionality.
    * Changed ordering of arguments for the following functions as they
      did not match the underlying C function signatures:

        * :issue:`130` - :func:`pywincffi.kernel32.events.CreateEvent`
        * :issue:`131` - :func:`pywincffi.kernel32.pipe.CreatePipe`
        * :issue:`133` - :func:`pywincffi.kernel32.process.CreateProcess`

    * :issue:`134` / :issue:`137` - Use str.format(), and unicode string
      literals in a few places.
    * :issue:`138` - Improvements to :class:`pywincffi.exceptions.WindowsAPIError`
      to better facilitate debugging.
    * :issue:`140` - Added constant ``ERROR_BAD_EXE_FORMAT``, a required
      constant by Twisted.

0.4.0
~~~~~

Notable enhancements and changes are:

    * Addition of :func:`pywincffi.kernel32.process.CreateProcess`,
      :func:`pywincffi.kernel32.overlapped.GetOverlappedResult` and
      several structures.  Implemented for :issue:`69`.
    * Reworked the test setup steps so they're more consistent.
    * Added a cleanup step to the tests to track down cases that were not
      resetting or testing the Windows API error code.
    * Cleaned up the setUp step in the base test case.
    * Added error constant ``ERROR_INVALID_HANDLE``.
    * :func:`pywincffi.kernel32.pid_exists` will no longer result in the
      Windows API error code being set to a non-zero value after exiting the
      function.
    * General code cleanup in a few of the core modules.
    * Removed an installation dependency: enum34

0.3.1
~~~~~

Notable enhancements and changes are:

    * :issue:`81` - :func:`pywincffi.user32.synchronization.WSAEventSelect` and
      :func:`pywincffi.user32.synchronization.WSAEnumNetworkEvents`
    * Removal of the ``pywincffi.core.config`` module in :issue:`107`.  The
      module was mostly unused internally and was not being used as part of
      the public APIs either.
    * Improvements to the :mod:`pywincffi.core.dist` module in :issue:`106`.
      This change allows pywincffi to add constants, functions, etc to the
      loaded library when :func:`pywincffi.core.dist.load` is called.  Before
      certain constants, such as ``ERROR_INVALID_HANDLE``, had to be imported
      from other modules rather than used directly from the library object.

0.3.0
~~~~~

Notable enhancements and changes are:

    * Added the :func:`pywincffi.kernel32.CreateToolhelp32Snapshot` function
      in :issue:`101`.
    * Fixed a bug where :func:`pywincffi.checks.input_check` might raise
      ``ffi.error`` in :issue:`73`
    * Several enhancements bringing :issue:`69` closer to closure.
    * Addition several functions for :issue:`69`:
        * :issue:`70` - :func:`pywincffi.kernel32.events.CreateEvent` and
          :func:`pywincffi.kernel32.events.OpenEvent`
        * :issue:`75` - :func:`pywincffi.kernel32.events.ResetEvent`
        * :issue:`76` - :func:`pywincffi.kernel32.process.TerminateProcess`
        * :issue:`78` - :func:`pywincffi.kernel32.handle.DuplicateHandle`
        * :issue:`79` - :func:`pywincffi.kernel32.process.ClearCommError`
        * :issue:`80` - :func:`pywincffi.user32.synchronization.MsgWaitForMultipleObjects`
    * Added Python 3.5 support to the build.  No bug fixes or code changes
      where required, just a minor test modification.
    * All exposed APIs updated to use the new Windows equivalent Python types
      in :mod:`pywincffi.wintypes`.
    * All exposed APIs now explicitly require either text or binary data.
    * Added FOREGROUND_RED, FOREGROUND_GREEN and FOREGROUND_BLUE constants in
      :issue:`95`.
    * Improved documentation for :class:`pywincffi.exceptions.InputError` and
      added the ability to generate custom error messages.

0.2.0
~~~~~

This release contains several enhancements, bug fixes and other
changes.  You can see all of the major issues by viewing the milestone
on GitHub: https://github.com/opalmer/pywincffi/issues?q=milestone:0.2.0.

Notable enhancements and changes are:

    * Improved error handling which brings more consistent error messages with
      better information.
    * Several new Windows API function implementations including
      FlushFileBuffers, CreateFile, LockFileEx, UnlockFileEx, MoveFileEx,
      GetProcessId, and GetCurrentProcess.
    * New wrapper function pid_exists().
    * Refactored kernel32 module structure.
    * Several bug fixes to existing tests and functions.
    * Updated developer documentation to better cover code reviews, style,
      functions, etc.
    * Fixed broken urls in `PyCharm Remote Interpreter` section of vagrant
      documentation for developers.
    * Added :func:`pywincffi.kernel32.handle.GetHandleInformation` and
      :func:`pywincffi.kernel32.handle.SetHandleInformation` in
      :issue:`66` - Thanks exvito!

0.1.2
~~~~~

Contains a fix to ensure that the proper version of ``cffi`` is
installed.  See https://github.com/opalmer/pywincffi/pull/45 for more
detailed information.  This release also includes a fix to the internal
release tool.

0.1.1
~~~~~

The first public release of pywincffi.  The
`GitHub release <https://github.com/opalmer/pywincffi/releases/tag/0.1.1>`_
contains the full list of issues, changes and pull requests.  The primary
purpose of this release was to end up with the tools and code necessary to
begin integrating pywincffi into Twisted.


0.1.0
~~~~~

This was an internal test release.  No data was published to PyPi or GitHub.

