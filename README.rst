Python Windows Wrapper Using CFFI
=================================

.. image:: https://ci.appveyor.com/api/projects/status/dl0ec1fny9keo61c/branch/master?svg=true
    :target: https://ci.appveyor.com/project/opalmer/pywincffi/history
    :alt: build status

.. image:: https://travis-ci.org/opalmer/pywincffi.png?branch=master
    :target: https://travis-ci.org/opalmer/pywincffi
    :alt: build status (pylint and pep8)

.. image:: https://readthedocs.org/projects/pywincffi/badge/?version=latest
    :target: http://pywincffi.readthedocs.org/en/latest/?badge=latest
    :alt: documentation badge


This library is a wrapper around some Windows functions using Python
and CFFI.  The repository was originally created to assist the Twisted
project in moving away from pywin32 so installation does not require a compile
step.

That said, contributions to this project to expand on the functionality are
always welcome.


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
