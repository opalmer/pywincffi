Code Review
===========

This document gives a basic overview of code reviews for the pywincffi
projects.  All code reviews are performed on GitHub by using pull
requests.  Information about pull requests and how to submit one can be found
here:

    https://help.github.com/articles/using-pull-requests/

What branch should I use?
-------------------------

You should always base your code from the master branch unless you've been
told otherwise.  The master branch should be considered production ready and
other branches are usually for testing and development.

What Will Be Reviewed
---------------------

    * If a new function is being added, review the `function <functions.html>`_
      documentation and make sure the new code matches these expectations.
    * For style issues, the default rule of thumb is to follow PEP8 unless it's
      something Windows specific.  Then, the `function <functions.html>`_
      documentation should be referenced.
    * Does the new function include documentation?  Are there comments for
      special cases?
    * Tests - Generally speaking, most changes should include a combination of
      unit and integration like tests.  Just calling the functions and ensuring
      they don't raise errors is sometimes ok but it's usually best to also
      ensure that the function works under 'real life' conditions.  For example
      if you are testing file locking, try accessing the file in another
      process.


Pre-Merge Requirements
----------------------

The following are required before a pull request can normally be merged:

    * All conflicts with the target branch should be resolved.
    * The unittests, linters and other checks run on AppVeyor must pass.
    * There should not be any major drops in coverage.  If there are it will
      be up to the reviewer(s) if the pull request should merge.
    * A brief description of the changes should be included in
      ``docs/changelog.rst`` under the 'latest' version.
    * Breaking changes should not occur on minor or micro versions unless the
      existing behavior can be preserved somehow.
