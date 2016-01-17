Python Windows Wrapper Using CFFI
=================================

.. image:: https://ci.appveyor.com/api/projects/status/dl0ec1fny9keo61c/branch/master?svg=true
    :target: https://ci.appveyor.com/project/opalmer/pywincffi/history
    :alt: build status

.. image:: https://travis-ci.org/opalmer/pywincffi.png?branch=master
    :target: https://travis-ci.org/opalmer/pywincffi
    :alt: build status (pylint and pep8)

.. image:: https://codecov.io/github/opalmer/pywincffi/coverage.svg?branch=master
    :target: https://codecov.io/github/opalmer/pywincffi?branch=master
    :alt: code coverage

.. image:: https://readthedocs.org/projects/pywincffi/badge/
    :target: https://pywincffi.readthedocs.org/
    :alt: documentation badge


``pywincffi`` is a wrapper around some Windows API functions using Python
and the `cffi <https://cffi.readthedocs.org>`_ library.  This project was
originally created to assist the Twisted project in moving away from its
dependency on ``pywin32``.  Contributions to expand on the APIs which pywincffi
offers are always welcome however.

The core objectives and design principles behind this project are:

    * It should be easier to to use Windows API functions both in terms of
      implementation and distribution.
    * Python 2.6, 2.7 and 3.x should be supported from a single code base and
      not require a consumer of pywincffi to worry about how they use the
      library.
    * Type conversion, error checking and other 'C like' code should be the
      responsibility of the library where possible.
    * APIs provided by pywincffi should mirror their Windows counterparts as
      closely as possible so the MSDN documentation can be more easily used as
      reference.
    * Documentation and error messages should be descriptive, consistent,
      complete and accessible.  Examples should be provided for more complex
      use cases.
    * For contributors, it should be possible to develop and test regardless
      of what platform the contributor is coming from.


Development
===========

Python Version Support
----------------------

This project supports Python 2.6 and up including
Python 3.  PRs, patches, tests etc that don't include
support for both 2.x and 3.x will not be merged.  The
aim is also the support both major versions of Python within
the same code base rather than rely on tools such as 2to3.

Documentation
-------------

The documentation for this this library is hosted on
`Read The Docs <https://pywincffi.readthedocs.org/>`_.
It's generated directly from this library using sphinx::

    virtualenv env
    env/bin/activate
    PYWINCFFI_INSTALL_BUILD=1 pip install -e .
    cd docs
    make html

Function Documentation
~~~~~~~~~~~~~~~~~~~~~~

Windows API Functions are typically documented in the following format:

.. code-block:: python

    def DuplicateHandle(arg1):
        """
        A brief message about this function.

        :param type arg1:
            Brief information about this argument

        .. seealso::

            <url to the MSDN API documentation for this function>
        """

It's important to note that the docs also contain a ``seealso`` link which
points back to the original documentation provided by Microsoft.  The link will
contain more detailed information about a function's specific behaviors and
caveats than pywincffi's docs may provide alone.


Testing
-------

Tests are located in the ``tests/`` directory.  The tests
themselves are run using ``nosetests`` either manually or using
the ``setup.py`` file::

    virtualenv env
    env/bin/activate
    pip install -e .
    python setup.py test

Every commit and pull request is also executed on
`AppVeyor <https://ci.appveyor.com/project/opalmer/pywincffi>`_.  Tests can also
be executed manually as well::

    nosetests -v --with-coverage

You can also follow `the documentation <https://pywincffi.readthedocs.org/en/latest/dev/vagrant.html>`_
and use Vagrant to test locally on non-Windows platforms.
