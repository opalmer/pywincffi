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

.. image:: https://readthedocs.org/projects/pywincffi/badge/?version=0.3.1
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

This section gives a basic overview of the development process including
the major goals.  This is not comprehensive but should be a good
introduction before submitting a pull request.

Support and Documentation
-------------------------

Besides this readme there are two other locations you can go to receive some
help:

    * https://pywincffi.readthedocs.org/en/latest/dev/ - Goes beyond
      what's in this readme.
    * https://groups.google.com/forum/#!forum/pywincffi - Google group for
      discussions, questions, etc.

Python Version Support
----------------------

This project supports Python 2.6 and up including Python 3.x.  PRs, patches,
tests etc that don't include support for both 2.x and 3.x will not be
merged.  The aim is also the support both major versions of Python within
the same code base rather than rely on tools such as 2to3, six or other
libraries for the most part.

Documentation
-------------

The documentation for this this library is hosted on
`Read The Docs <https://pywincffi.readthedocs.org/>`_.
It's generated directly from this library using sphinx::

    virtualenv env
    env/bin/activate
    pip install -r dev_requirements.txt
    pip install -e .
    cd docs
    make html

The build process also builds the documentation to ensure there are not
any obvious problems (including broken links).

Function Documentation
~~~~~~~~~~~~~~~~~~~~~~

Windows API Functions are typically documented in the following format:

.. code-block:: python

    def DuplicateHandle(arg1, kwarg1=None):
        """
        A brief message about this function.

        .. seealso::

            <url to the MSDN API documentation for this function>

        :param type arg1:
            Brief information about this argument

        :keyword type kwarg1:
            Brief information about this keyword include it's default
            and how it's handled within the function.

        :raises SomeException:
            Some information on when this exception will be raised

        :rtype: type
        :return:
            Information about the data that's returned
        """

It's important to note that the docs contain a ``seealso`` stanza.  This is
typically used to reference the MSDN documentation but may also be used to
reference examples, white papers or other reference which may be useful in
describing the function.

Adding new functions is covered in greater detail
`here <https://pywincffi.readthedocs.org/en/latest/dev/functions.html>`_


Testing
-------

Nosetests
~~~~~~~~~
Tests are located in the ``tests/`` directory.  The tests
themselves are run using ``nosetests`` either manually or using
the ``setup.py`` file::

    virtualenv env
    env/bin/activate
    pip install -r dev_requirements.txt
    pip install -e .
    nosetests tests

Continuous Integration
~~~~~~~~~~~~~~~~~~~~~~

To consistently ensure the highest quality code, the following services are
utilized to test or analyze every commit and pull request:

    * `AppVeyor <https://ci.appveyor.com/project/opalmer/pywincffi>`_ - Runs
      the unittests, builds wheel files, MSIs and other output artifacts
      which can be published in a release.
    * `Travis <https://travis-ci.org/opalmer/pywincffi>`_ - Runs the ``pep8``
      and ``pylint`` command line tools on the code base and tests.  This also
      builds the docs so documentation problems are easily spotted.
    * `Codecov <https://codecov.io/github/opalmer/pywincffi>`_ - Analyses and
      displays code coverage results after tests have run on AppVeyor.  Results
      are posted back to pull requests.
    * `ReadTheDocs <https://readthedocs.org/projects/pywincffi/builds/>`_. -
      The official location where documentation is built and posted.  This is
      generally for merges into the master branch however.

Additional Testing
~~~~~~~~~~~~~~~~~~

As seen above, there are numerous tests besides the unittests.  To run all
the tests on Windows, much like the continuous integration systems do, you can
run ``test.bat``:

.. code-block:: console

    > test.bat
    ========================================================================================
    pep8 pywincffi
    ========================================================================================
    ========================================================================================
    pep8 tests
    ========================================================================================
    ========================================================================================
    pylint pywincffi
    ========================================================================================
    ========================================================================================
    pylint tests
    ========================================================================================
    ========================================================================================
    sphinx-build -q -b html -W -E -a -d docs/build/doctrees docs/source docs/build/html
    ========================================================================================
    ========================================================================================
    sphinx-build -q -b linkcheck -W -E -a -d docs/build/doctrees docs/source docs/build/html
    ========================================================================================
    ========================================================================================
    setup.py bdist_wheel
    ========================================================================================
    RuntimeWarning: Config variable 'Py_DEBUG' is unset, Python ABI tag may be incorrect
      warn=(impl == 'cp')):
    RuntimeWarning: Config variable 'WITH_PYMALLOC' is unset, Python ABI tag may be incorrect
      warn=(impl == 'cp')):
    ========================================================================================
    nosetests -sv tests
    ========================================================================================
    [ omitted ]
    ========================================================================================


Keep in mind that this will not setup the virtualenv or build environment for
you.  So if you can't build the library or are missing a dependency then
the above may fail.


Vagrant
~~~~~~~

The continuous integration services above negate most of the need to setup
your local workstation to handle development for pywincffi, even if you're not
running Windows.  In some cases however it can be faster or easiear to work
on your local machine.

If you're not running Windows or you don't have the tools necessary to
develop pywincffi on your machine you can use
`Vagrant <https://www.vagrantup.com/>`_ to build a Windows machine and start
developing.  There's a more in depth explanation of this process located
here:

    https://pywincffi.readthedocs.org/en/latest/dev/vagrant.html
