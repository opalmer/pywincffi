Python Windows Wrapper Using CFFI
=================================

This library is a wrapper around some Windows functions using Python 
and CFFI.  The repository was originally created to assit the Twisted
project in moving away from pywin32 so install requirements don't
require a manual install or compile step.

Contributions to this project to expand on the features it provides
or to add new ones is always welcome.




Development
===========

.. note::

    This section is under development and may not 
    represent the current state of the repository.

Python Version Support
----------------------

This project supports Python 2.6 and up including 
Python 3.  PRs, patches, tests etc that don't include
support for both 2.x and 3.x will not be merged.  The 
aim is also the support both major versions of Python within
the same code base rather than rely on tools such as 2to3.

Documentation
-------------

Documentation should be provided as reStructuredText both for
inline documentation and documentation that lives under ``doc/``
directory.  

The built documentation for this project will lives here:

    https://pywincffi.readthedocs.org


Testing
-------

Tests are located in the ``tests/`` directory.  The tests
themselves are run using ``nosetests``.  Although, you could
use other runners too as the only library used by the tests 
is ``unittests``.

Because this is a Windows based project all tests must pass
on Windows.  Some tests may work on non-Windows platforms but
no tests may be exclusivly for non-windows platforms.

.. note::

   A commit hook will be setup so that all PRs are tested
   and run before they are marked as 'green'.  This is 
   similiar to the approach used by Travis to sign off
   on a PR based on the results of a test run.
