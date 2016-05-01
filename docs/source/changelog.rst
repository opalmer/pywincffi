Changelog
=========

This document contains information on pywincff's release history.  Later
versions are shown first.


Versions
--------

latest
~~~~~~

Notable enhancements and changes are:

    * Fixed a bug where :func:`pywincffi.checks.input_check` might raise
      ``ffi.error`` in :issue:`73`
    * Several enhancements bringing :issue:`69` closer to closure.
    * Addition several functions or :issue:`69`:
        * :issue:`70` - :func:`pywincffi.kernel32.events.CreateEvent` and
          :func:`pywincffi.kernel32.events.OpenEvent`
        * :issue:`75` - :func:`pywincffi.kernel32.events.ResetEvent`
        * :issue:`76` - :func:`pywincffi.kernel32.process.TerminateProcess`
        * :issue:`78` - :func:`pywincffi.kernel32.handle.DuplicateHandle`
        * :issue:`79` - :func:`pywincffi.kernel32.process.ClearCommError`

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

