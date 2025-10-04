.. _contributing:

Contributing to archeryutils
============================

*archeryutils* is a free open-source project to which anyone can contribute code.
If you encounter and/or fix a bug or implement a few feature please contribute it
back to the core codebase. Alternatively, if you are want to get involved but are
unsure where to start take a look at the
`open issues <https://github.com/jatkinson1000/archeryutils/issues>`_ to see if there
is anything you could tackle.

.. contents:: Contents:
   :local:
   :depth: 1

.. note::

  Parts of this document are based on the 
  `xarray contributing guide <https://docs.xarray.dev/en/stable/contributing.html>`_
  which itself is heavily based on the 
  `Pandas Contributing Guide <http://pandas.pydata.org/pandas-docs/stable/contributing.html>`_.


.. _issues:

Bug Reports and Feature Requests
--------------------------------

Bug reports are an important part of making *archeryutils* more stable.
Having a complete bug report allows others to reproduce the bug and provides insight
into fixing.

Trying out the bug-producing code on the main branch is often a worthwhile exercise
to confirm that the bug still exists.
It is also worth searching existing bug reports and pull requests to see if the issue
has already been reported and/or fixed.


Submitting a bug report
~~~~~~~~~~~~~~~~~~~~~~~

If you find a bug in the code or documentation, do not hesitate to submit a ticket to the
`Issue Tracker <https://github.com/jatkinson1000/archeryutils/issues>`_.

When reporting a bug, please include the following:

#. A short, self-contained Python snippet reproducing the problem.
   You can format the code nicely by using `GitHub Flavored Markdown
   <http://github.github.com/github-flavored-markdown/>`_::

      ```python
      import archeryutils as au

      myTarget = au.Target(...)

      ...
      ```

#. Include the full version string of *archeryutils* and its dependencies.
   You can use the archeryutils ``versions()`` function::

      import archeryutils as au
      au.versions()

#. Explain why the current behavior is wrong/not desired and what you expect instead.

The issue will then show up to the *archeryutils* community and be open to
comments/ideas from others.

See this `stackoverflow article <https://stackoverflow.com/help/mcve>`_ 
for more detailed tips on writing a good bug report.

If you have fixed the issue yourself in your own version of *archeryutils* please note
this on the issue and follow up by opening a :ref:`pull request <pull_request>`.


Submitting a feature request
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If there is a feature you think would be useful to add to *archeryutils* please make
a request using the
`Issue Tracker <https://github.com/jatkinson1000/archeryutils/issues>`_.
When doing so please try to include the following details:

#. A clear description of the functionality you would like to see added and why you feel
   it would be useful.

#. Any external references that are helpful/required to understand and implement
   your request in detail.

#. A short code snippet indicating what the desired API might look like.

If you have already implemented the feature yourself in your own version of
*archeryutils* please note this on the issue and follow up by opening a
:ref:`pull request <pull_request>`.


Code Contributions
------------------

.. contents:: Contributing to the Codebase:
   :local:


.. _linting:

Coding standards and formatting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Writing good code is not just about what you write.
It is also about *how* you write it.
During continuous integration testing, several tools will be run to check your code
for stylistic errors.
Generating any warnings will cause these tests to fail.
Thus, good style is a requirement for submitting code to *archeryutils*.

*archeryutils* uses tools to ensure consistent and quality code formatting throughout:

- `ruff <https://docs.astral.sh/ruff/>`_ for:

  - standardized code formatting
  - code quality checks
  - checking docstrings against the numpy conventions

- `mypy <http://mypy-lang.org/>`_ for static type checking of
  `type hints <https://docs.python.org/3/library/typing.html>`_.

These will be checked on all pull requests and commits to main, so it is suggested you
run them on your code before committing.

This can be done with a development install by running the following bash commands from
the root directory:

.. code-block:: shell

    ruff format archeryutils
    ruff archeryutils
    mypy archeryutils

Sometimes it makes sense to
`disable a ruff warning <https://docs.astral.sh/ruff/linter/#error-suppression>`_.
We generally prefer that this is done on a case-by-case basis in the code.
If you have justification for turning off any warnings in your contribution please
document them in your pull request.
If you think a rule or ruleset should be more widely disabled for the project, please
open an issue or detail it in a pull request with a clear explanation.

The full *ruff* configuration for the project is contained in the 
`pyproject.toml <https://github.com/jatkinson1000/archeryutils/blob/main/pyproject.toml>`_
file.


.. _testing:

Testing
~~~~~~~

Testing is a vital yet often under-utilised aspect of writing good code.
At its most basic testing is important to verify that code is working correctly - we
can write a test to which we know what the output *should* be, and then compare the
results produced by the code to ensure it is doing what we intend it to.
Tests are also important for future development to ensure that any changes do
not break behaviour or have unintended consequences.
Since all previously written tests are archived with the code and are run for all new
contributions, it will quickly become apparent if behaviour changes anywhere.

*archeryutils* uses the `pytest <https://pytest.org>`_ framework for writing and
running tests.

To run the tests from a development install run, from the top directory::

    pytest archeryutils

which, if successful, should produce output that looks something like:

.. code-block:: shell

    $ pytest archeryutils
    ================================= test session starts =================================
    platform darwin -- Python 3.10.13, pytest-7.4.0, pluggy-1.2.0
    rootdir: /Users/home/archeryutils
    plugins: mock-3.11.1, anyio-3.7.1, xdist-3.5.0
    collected 343 items
    
    archeryutils/classifications/tests/test_agb_field.py .......................... [  7%]
    .....                                                                           [  9%]
    archeryutils/classifications/tests/test_agb_indoor.py ......................... [ 16%]
    ..............                                                                  [ 20%]
    archeryutils/classifications/tests/test_agb_old_indoor.py ..................... [ 26%]
                                                                                    [ 26%]
    archeryutils/classifications/tests/test_agb_outdoor.py ........................ [ 33%]
    ..........................                                                      [ 41%]
    archeryutils/classifications/tests/test_classification_utils.py ..........      [ 44%]
    archeryutils/handicaps/tests/test_handicap_tables.py .......................    [ 50%]
    archeryutils/handicaps/tests/test_handicaps.py ................................ [ 60%]
    ...................................................................             [ 79%]
    archeryutils/tests/test_constants.py ..............                             [ 83%]
    archeryutils/tests/test_rounds.py ....................                          [ 89%]
    archeryutils/tests/test_targets.py ....................................         [100%]

    ================================ 343 passed in 2.12s =================================


Writing tests
^^^^^^^^^^^^^

Full details and documentation for pytest can be found on the `pytest website <https://pytest.org>`_,
but a short overview is given here:

* Tests should be placed in their own files separate from the source code.
  They should be placed in a ``tests/`` subdirectory within each package and have
  filenames of the format ``test_<something>.py``.

* Tests are often class-based for organisation, with a test class containing all the
  tests pertaining to a particular class, method, etc.

* To run a single test on a variety of inputs use ``@pytest.mark.parameterize``.

* Use the ``assert`` statement to compare expected and actual outputs.
  For floating point comparisons apply the ``pytest.approx()`` function to the actual
  output.

We suggest reviewing the existing tests in the *archeryutils* codebase to get a feeling
for how things are structured and written.

When considering what tests to write for your contribution consider the following:

* Comparisons of basic usage to known outputs to ensure your code behaves as expected.

* Response to different optional input parameters to ensure they function as expected.

* Response to inappropriate inputs/usage to ensure that the correct failure behaviour
  occurs and the correct warnings/errors are raised.

* Checks for any `edge or corner cases <https://en.wikipedia.org/wiki/Edge_case>`_ that
  may occur in use. For *archeryutils* a classic example that shows up is the case
  of handling the maximum score for a particular round.

We aim for as much as possible of the *archeryutils* codebase to be covered by testing.
During continuous integration a
`coverage checker <https://app.codecov.io/gh/jatkinson1000/archeryutils>`_ will run
the tests and highlight any parts of the code that are not covered by tests.


.. _pull_request:

Opening a pull request
~~~~~~~~~~~~~~~~~~~~~~

If you have something to contribute to the *archeryutils* codebase this is done by
opening a pull request to the
`main repository on GitHub <https://github.com/jatkinson1000/archeryutils>`_.

Here is a summary of the expected workflow when contributing:

#. Make sure there is an open issue on the
   `Issue Tracker <https://github.com/jatkinson1000/archeryutils/issues>`_ as
   :ref:`described above <issues>` detailing the bug/feature that you are addressing.

#. `Fork the main repository <https://github.com/jatkinson1000/archeryutils/fork>`_
   into your own personal GitHub space, and then clone and work on this fork.
   You should work on a branch within this fork with a sensible name that reflects
   what you are working on.

#. As you work on the code, commit your changes in sensible-sized chunks with clear
   commit messages.
   A commit should detail any changes made to perform a particular action en route
   to the overall goal. When writing commit messages remember that it needs to be
   clearly understandable to other developers as to what they contribute.
   See previous commits in the project for examples.

   As you work keep the following aspects in mind:

   a. Do not place large changes to multiple files in a single commit.

   b. Try and remember to apply the :ref:`stylistic checks and balances <linting>`
      to your code before committing. You may consider using a
      `pre-commit hook <https://pre-commit.com/>`_ to help with this.

   c. Make sure that you include :ref:`appropriate tests <testing>` alongside your
      code contributions. Code without tests will not be merged.

   d. Make sure that you include/update any docstrings in the code, and that they
      conform to the `numpy style <https://numpydoc.readthedocs.io/en/latest/format.html>`_.
      See the rest of the code for examples.

   e. Make sure that you :ref:`update the documentation <docs_contributions>` where
      necessary to reflect the additions you have made. If adding a significant
      top-level feature to the code you may want to update the
      :ref:`getting started <quickstart>` pages and the *examples* notebook to showcase
      your additions.

#. Once you push code back to your GitHub fork you can open a pull request.
   For small bug-fixes and features you may wait until you feel things are complete
   before opening the pull request.
   However, if you wish for feedback/intermediate review then please open the pull
   request in draft mode during development.

#. When opening a pull request ensure that it contains:

   * A sensible title summarising its contribution.
   * A `reference <https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/autolinked-references-and-urls>`_
     to the issue number(s) that it is addressing.
   * The following checklist

      .. code-block:: markdown

         - [ ] Source code updated to address issue
         - [ ] Style and formatting applied
         - [ ] Tests written to cover changes
         - [ ] Docstrings included/updated in code
         - [ ] Project documentation updated as necessary

Once a pull request is opened it will be reviewed by the project maintainers and any
requests for changes/improvement fed back to the author.
Once the maintainers are happy, your code will be approved and the pull request merged!


.. _docs_contributions:

Documentation Contributions
---------------------------

If you’re not the developer type, contributions to the documentation are still of value.
If something in the docs doesn’t make sense to you, updating the relevant section
after you figure it out is a great way to ensure it will help the next person.
If you are not comfortable with the process detailed below, then please provide
feedback by :ref:`opening an issue <issues>` with the details.

The documentation is written in
`reStructuredText <https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html>`_
and built using Sphinx.
The `Sphinx Documentation <https://www.sphinx-doc.org/en/master/contents.html>`_
has an excellent
`introduction to reST <https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html>`_
in addition to other aspects of Sphinx.

The beauty of using Sphinx is that much of the API documentation can be automatically
generated from the docstrings in the source code.
This is why it is important to put time into these.

The rest of the documentation, such as the installation and getting started pages, and
the contribution guidelines that you are reading right now, are written out and stored
in the ``docs/`` directory of the code.

To build the documentation on a development install run::

    cd docs/
    make clean
    make html

This will generate HTML output files in the folder ``docs/_build/html/`` that can be
viewed in a browser.
