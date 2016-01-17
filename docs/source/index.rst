Welcome to PyWinCFFI's documentation!
=====================================

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

.. seealso::

    `PyWinCFFI's README <https://github.com/opalmer/pywincffi/blob/master/README.rst>`_

Main Index
==========

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Python Package
==============

.. toctree:: modules/modules.rst


Development
===========

.. toctree:: dev/index.rst