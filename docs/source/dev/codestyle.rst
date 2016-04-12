Coding Style and Conventions
============================

This document covers some specific coding conventions and style choices for
pywincffi that may not be covered by other development documentation.

Single vs. Double Quotes
------------------------

Python has two kinds of quotes, ``'`` and ``"``.  The language itself does not
treat the two any differently however other languages, like C, do. For the
purposes of pywincffi all strings should be constructed with ``"`` unless
there's a specific reason not to.  This is mostly for internal consistency but
also because "hello" is how you'd expect to see a string literal in C.
Though Python is not C pywincffi can and does deal with C APIs so it's less
of a cognitive jump to just stick with ``"``.

Windows Constants
-----------------

This project uses and reference a lot of constants in Windows.  For
consistency and readability we should always use Windows constants by name
rather than hard coding numbers.

For example if you're writing a test or code like this:

.. code-block:: python

   SetHandleInformation(handle, 1, 0)

Then it would be preferable to write:

.. code-block:: python

   _, library = dist.load()
   SetHandleInformation(handle, library.HANDLE_FLAG_INHERIT, 0)


