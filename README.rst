Python Windows Wrapper Using CFFI
=================================

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

It's important to note that the ``seealso`` link is an important part
of each function.  If you're looking to learn more about specific behaviors,
caveats or just more general information then follow the link to Microsoft's
documentation.


Testing
-------

Tests are located in the ``tests/`` directory.  The tests
themselves are run using ``nosetests`` either manually or using
the ``setup.py`` file::

    virtualenv env
    env/bin/activate
    pip install -e .
    python setup.py test

Every build is also executed on https://build.opalmer.com/ and you could
use ``nosetests`` directly if you wish as well::

    nosetests -v --with-coverage
