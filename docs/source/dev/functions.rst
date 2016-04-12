Functions
=========

This document provides detailed information on how to add new functions to
pywincffi and should be treated as a general guide as the implementation may
vary between functions.

Adding A New Windows Function
-----------------------------

This section walks through adding a new Windows function, WriteFile, including
some of the best practices on how to handle user input.  As stated at the top
of this documentation, these practices will likely vary some from function to
function.

Function Definition
~~~~~~~~~~~~~~~~~~~

There are two parts to defining a new function.  You must define the
function in Python to wrap the underlying library function and you must
define the function the C header so the function can be called in Python so
consider this a guide book more than a set of rules.

C Header
++++++++

The C header for function definitions is located in
:blob:`pywincffi/core/cdefs/headers/functions.h` and is sometimes referred to
the 'cdef'. When creating a new function you should essentially match what the
msdn documentation defines.  If you're implementing `WriteFile` for example
you'd look at :msdn:`aa365747` and translate this to:

.. code-block:: c

   BOOL WriteFile(HANDLE, LPCVOID, DWORD, LPDWORD, LPOVERLAPPED);

It's important to note here that all inputs, output, optional arguments, etc
are included in the header definition even if you don't plan on exposing them
from the Python wrapper.

Location of C Definitions
`````````````````````````

Currently all C definitions reside in
:blob:`pywincffi/core/cdefs/headers/functions.h`.  Unlike the Python wrapper
functions, which are discussed below, the C definition is not exposed to
downstream consumers. The structure of the C definition files also does not
impact how the wrapper functions are structured either since both pywincffi and
the downstream consumers consume from :func:`pywincffi.core.dist.load`.

The C definition files could be better organized in the future if necessary.
As it stands today this would only require minor changes to the
`HEADER_FILES` and `SOURCE_FILES` globals in :mod:`pywincffi.core.dist`.

Python
++++++

Constructing The Wrapper
````````````````````````

In order to make a Windows function available you need to write a 'wrapper'
function. Technically speaking it's not a requirement in order to call the
underlying C function however it makes the process of calling into
a C function much easier for a consumer of pywincffi.

Getting back to the `WriteFile` example above and the :msdn:`aa365747` article
from msdn, WriteFile has a few input and outputs


.. code-block:: c

   BOOL WINAPI WriteFile(
     _In_        HANDLE       hFile,                  // input (required)
     _In_        LPCVOID      lpBuffer,               // input (required)
     _In_        DWORD        nNumberOfBytesToWrite,  // input (required)
     _Out_opt_   LPDWORD      lpNumberOfBytesWritten, // output (optional)
     _Inout_opt_ LPOVERLAPPED lpOverlapped            // input/output (optional)
   );


When approaching a function like this, ask a few basic questions to compare
the C implementation to Python:

   * How do you write data to a file in Python?
   * What arguments are required when you write data?
   * What do you get out of the function(s) that can write data to a file?
   * Are there functions in Python which are similar to the function being
     defined?

So in Python, the following input arguments are not normally required because
Python typically handles them for you:

   * **lpBuffer** - A buffer containing the data to write
   * **nNumberOfBytesToWrite** - The number of bytes you intend to write

The only function which is similar to `WriteFile` is :func:`os.write` which
takes a file descriptor and data to be written and returns the number of bytes
written.  So our implementation of `WriteFile` should be similar.  In fact,
it can look almost identical:

.. code-block:: python

   def WriteFile(hFile, lpBuffer): # -> bytes written
       pass


However since we're wrapping a Windows function and shouldn't artificially
limit access to the underlying Windows API what should really be defined is:

.. code-block:: python

   def WriteFile(
       hFile, lpBuffer,
       nNumberOfBytesToWrite=None, lpOverlapped=None): # -> bytes written
       pass

Here's how the individual arguments would be handled inside of the function:

   * **hFile** - A Windows handle must be created before being passed in.  There
     is the :func:`pywincffi.kernel32.handle_from_file` function to help with
     going from a Python file object to Windows handle object.
   * **lpBuffer** - String, bytes and unicode are converted to the appropriate
     C type before being passed to the C call.
   * **nNumberOfBytesToWrite** - Can be determined from the size of lpBuffer or
     an integer can be provided.
   * **lpOverlapped** - Optional according to msdn but someone can pass in
     their own overlapped structure if they wanted.


Location Of Wrapper Function
````````````````````````````

For the most part what module you decide to place `WriteFile` in is up to
you however the module should be related to the function. `WriteFile` is meant
to operate on files so it makes sense to include it in a `file` module.  In
Windows the `kernel32` library defines `WriteFile` so the subpackage the wrapper
belongs to is also called `kernel32`::

    pywincffi.kernel32.file.WriteFile <---- wrapper function
        ^         ^     ^
        |         |     |
      Root        |     |
     Package      |     |
            Subpackage/ |
            Windows Lib |
                        |
                   Object Type
                       or
                 Operation Group

New functions which come from other Windows modules should add new top
level subpackages.

Import Structure
````````````````

In many Python programs, full import paths are often encouraged.  So to import
`WriteFile` one would do:

.. code-block:: python

   from pywincffi.kernel32.file import WriteFile

Internally within pywincffi, the above import path should be used. External
consumers of pywincffi would import the function like this:

.. code-block:: python

   from pywincffi.kernel32 import WriteFile

So when you add a new function be sure to add it to the `__init__.py` for
the subpackage.  This ensures that if the import structure has to change
within one of pywincffi's modules we're less likely to break downstream
consumers.




Argument and Keyword Naming Conventions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If an argument or keyword is intended to be an analog for an argument to
a Windows API call then it should follow the same naming convention as
the documented function does. The `WaitForSingleObject` function for example
takes two arguments according to the MSDN documentation which when translated
to Python would look like this:

.. code-block:: python

   def WaitForSingleObject(hHandle, dwMilliseconds):
       pass

Any argument or keyword which is not directly related to an input to a Windows
API should instead use the standard PEP8 naming conventions:

.. code-block:: python

   def WaitForSingleObject(hHandle, dwMilliseconds, other_keyword=None):
       pass


Internal Variables
~~~~~~~~~~~~~~~~~~

Like arguments or keywords variables should be named either using `camelCase`
if they're intended to map to a value passed into a Windows API call or using
the `name_with_underscores` convention in other cases.  Here's an example of
the two:

.. code-block:: python

   def UnlockFileEx(...):

        # internal variables
        ffi, library = dist.load()

        # lpOverlapped is a Windows structure
        if lpOverlapped is None:
            lpOverlapped = ffi.new("OVERLAPPED[]", [{"hEvent": hFile}])


Documentation
-------------

This section covers the basics of documenting functions in pywincffi.  The
below mostly applies to how Windows functions should be documented but should
generally apply elsewhere in the project too.

Basic Layout
~~~~~~~~~~~~

The layout of the documentation string for each function should be consistent
throughout the project.  This generally makes it easier to understand but also
harder to miss more critical information.  Below is an annotated example
of a fake Windows function:

.. code-block:: python

   def AWindowsFunction(...):
       """
       First few sentences should tell someone what AWindowsFunction
       does.  This can usually be pulled from the MSDN documentation but
       is usually shorter and more concise.

       .. seealso::

          <url pointing to the msdn reference for AWindowsFunction>
          <url pointing to a use case or other useful information>

       :param <python type> variable_name:
           Some information about what variable_name is.  Again, can be pulled
           from the msdn documentation but should be concise as someone can
           always go read the msdn documentation.  This information should
           always state key differences, if there are any, between what
           the C api call normally expects and what the wrapper does.

       <additional keyword or argument documentation>

       :raises SomeException:
           Information about under what condition(s) SomeException may be
           raised.  SomeException should be something that's raised directly
           by AWindowsFunction.


       :rtype: <The python type returned.  Required if different from the msdn docs>
       :returns:
           Some information about the return value.  This part of the
           documentation should be excluded if the function does not
           return anything.
       """




Arguments and Keywords
~~~~~~~~~~~~~~~~~~~~~~

Position arguments should be documented using ``:param <type> name:`` while
keywords should be documented using ``:keyword <type> name:``.  The ``<type>``
is referring to the Python type rather than the Windows type which
the argument may be an analog for.  Here's a simplified example:

.. code-block:: python

   def CreateFile(lpFileName, dwDesiredAccess, dwShareMode=None ...):
       """
       :param str lpFileName:

       :param int dwDesiredAccess:

       :keyword int dwShareMode:
       """

It's possible to allow an input argument to support multiple types as well:

.. code-block:: python

   def foobar(arg1):
       """
       :type arg1: int or str
       :param arg1:
       """

If the argument or keyword you are documenting requires some additional setup,
such initializing a struct, it can be helpful to include a real example:

.. code-block:: python

   def CreatePipe(lpPipeAttribute=None):
       """
       ...

       :keyword struct lpPipeAttributes:
           The security attributes to apply to the handle. By default
           ``NULL`` will be passed in meaning then handle we create
           cannot be inherited.  Example struct:

           >>> from pywincffi.core import dist
           >>> ffi, library = dist.load()
           >>> lpPipeAttributes = ffi.new(
           ...     "SECURITY_ATTRIBUTES[1]", [{
           ...     "nLength": ffi.sizeof("SECURITY_ATTRIBUTES"),
           ...     "bInheritHandle": True,
           ...     "lpSecurityDescriptor": ffi.NULL
           ...     }]
           ... )
       """


External References
~~~~~~~~~~~~~~~~~~~

External references, such as those referencing the msdn documentation, are
usually included within a ``.. seealso::`` block.  For msdn documentation,
this structure is usually preferable:

.. code-block:: rst

   .. seealso::

      https://msdn.microsoft.com/en-us/library/<article_number>


.. note::

   The documentation build, which is run for every commit, checks to ensure
   that the documents being referenced do in fact exist.  If the url can't
   be reached the build will fail.


Handling Input
--------------

One of the main goals of pywincffi is to provide are more Python like interface
for calling Windows APIs.  To do this the pywincffi functions implement type
checking, conversion and argument handling so less work is necessary on the
consumer's part.

Type Checking
~~~~~~~~~~~~~

In order to provide better error messages and more consistent expectations of
input arguments each function should perform type checking on each argument.
Most type checks are run using the :func:`pywincffi.core.checks.input_check`
function:

.. code-block:: python

   from six import integer_types
   from pywincffi.core.checks import input_check

   def Foobar(arg1, arg2):
       input_check("arg1", arg1, integer_types)
       input_check("arg1", arg2, allowed_values=(1, 2, 3))

If :func:`pywincffi.core.checks.input_check` does not do what you need or
you have to perform multiple steps to validate an input argument you can raise
the :class:`pywincffi.exceptions.InputError` exception yourself.

.. note::

   There are some enums to help with special cases (file handles, structure,
   etc) and more can be added.  See :blob:`pywincffi/core/checks.py`


Type Conversion
~~~~~~~~~~~~~~~

The underlying library that pywincffi uses, cffi, can do most type conversions
for you.  While normally this will function as you'd expect it's better to be
explicit and handle the conversion yourself so there are fewer surprises.

Here's an example of how an 'automatic' conversion would look:

.. code-block:: python

   library.LockFileEx(hFile, 0, 0, 0, 0, lpOverlapped)


The problem is it makes it easier to pass something into `LockFileEx` that
cffi might not know how to convert.  The error produced as a result may look
strange to someone unfamiliar with cffi and it could be more difficult to debug
as result.

To avoid this problem pywincffi should try to perform the cast manually before
making calls to the underlying API call.  This ensures that cffi shouldn't need
to do the conversion itself and limits the chance of lower level errors
propagating:

.. code-block:: python

   library.LockFileEx(
      hFile,
      ffi.cast("DWORD", 0),
      ffi.cast("DWORD", 0),
      ffi.cast("DWORD", 0),
      ffi.cast("DWORD", 0),
      lpOverlapped
   )


Keywords
~~~~~~~~
In C, there's not really an equivalent to a keyword in Python.  However for
many of the Windows API functions the msdn documentation may say something
along the lines of *This parameter can be NULL.*  For pywincffi, reasonable
default values should be defined where possible so not every argument is
always required.

As an example the `lpSecurityAttributes` argument for `CreateFile`
can be `NULL` and would be handled like this:

.. code-block:: python

   def CreateFile(..., lpSecurityAttributes=None):
      ffi, library = dist.load()

      if lpSecurityAttributes is None:
         lpSecurityAttributes = ffi.NULL


.. attention::

   Be sure that if a keyword is in fact required in some cases but not
   others that you raise InputError when the required keyword is not
   provided.


Handling Output
---------------

Many Windows functions have a return value and some return values will be stored
in another variable rather returned directly from the API call.  This section
tries to detail a couple of different cases and how to handle them.

Windows API Error Checking
~~~~~~~~~~~~~~~~~~~~~~~~~~

When calling a Windows function it's the responsibility of the wrapper function
in pywincffi to check for errors using the
:func:`pywincffi.core.checks.error_check` function:

.. code-block:: python

   from pywincffi.core.checks import Enums, error_check

   def WriteFile(...):
      code = library.WriteFile(
           hFile, lpBuffer, nNumberOfBytesToWrite, bytes_written, lpOverlapped)
       error_check("WriteFile", code=code, expected=Enums.NON_ZERO)

This ensures that when an API does fail pywincffi will raise a consistent error
with as much information as possible to help the consumer of the API determine
what the problem is.


API Return Values
~~~~~~~~~~~~~~~~~

If a function returns a handle, structure, etc it's usually best to return this
from the wrapper function too.  Be sure the wrapper functions's documentation
provides an example if accessing or using the data requires a couple of extra
steps.


Windows Constants
-----------------

When it comes to Windows constants code in Python you'll often seen one
of two kinds of definitions:

.. code-block:: python

   FILE_ATTRIBUTE_ENCRYPTED = 0x4000  # matches the msdn reference
   FILE_ATTRIBUTE_ENCRYPTED = 16384  # same as the above but turn into an int

While neither of these are incorrect there are a few problems with making
constants this way:

   * It's easy to insert a typo into a variable name or its value.
   * You have to rely on code review to check for correctness.
   * They're not true constants and could be modified at runtime.

So in pywincffi, we usually define constants in
:blob:`pywincffi/core/cdefs/headers/constants.h`. At compile time any typos
will result in build errors and the values are replaced when the library is
compiled.


Adding New Constants
~~~~~~~~~~~~~~~~~~~~

To add a new constant, simply define a line in
:blob:`pywincffi/core/cdefs/headers/constants.h`:

.. code-block:: c

   #define FILE_ATTRIBUTE_ENCRYPTED ...

When should new constants be defined?  It varies but it's good general
practice to define all of the constants mentioned in the msdn documentation
for the function you are working on.  So for example if you're working on
the ``SetHandleInformation`` function the documentation at :msdn:`ms724935`
would have you define two constants as a result:

.. code-block:: c

   #define HANDLE_FLAG_INHERIT ...
   #define HANDLE_FLAG_PROTECT_FROM_CLOSE ...


Using Existing Constants
~~~~~~~~~~~~~~~~~~~~~~~~

When developing code for pywincffi, either within the library itself or the
tests, constants should be used instead of default values.  To access a
defined constant you'll need to load the library:

.. code-block:: python

   from pywincffi.core import dist
   _, library = dist.load()
   library.FILE_ATTRIBUTE_ENCRYPTED
