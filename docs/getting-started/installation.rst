.. _installing:

Installation
============

Required dependencies
---------------------

- Python (3.10 or later)
- `numpy <https://www.numpy.org/>`__ (1.20 or later)
- `aenum <https://pypi.org/project/aenum/>`__ (Python versions < 3.12)

.. _optional-dependencies:

Installation Instructions
-------------------------

archeryutils is a pure python package.
It can be installed using pip by executing::

    pip install archeryutils

Development Installation
------------------------

To install as a developer you should clone the repository from the online repo and
install as an editable package::

    git clone git@github.com:jatkinson1000/archeryutils.git
    cd archeryutils
    pip install -e .[dev]

.. note::
   If you are installing in zsh you will need to use quotes for the optional dependencies:

   .. code-block:: bash

      pip install -e '.[dev]'

The `dev` optional dependencies combine the `test`, `lint`, and `docs` subgroups
detailed below.

Testing
~~~~~~~

The test suite for archeryutils makes use of `pytest <https://docs.pytest.org/>`__.
To run tests on a development installation run::

    pytest ./

from within the base directory.

Optional dependencies
~~~~~~~~~~~~~~~~~~~~~

archeryutils has a series of optional dependencies that can be installed:

test
^^^^

For developing and running the test suite on the code::

    pip install -e .[test]

* pytest (7.2.0 or later)
* pytest-mock

lint
^^^^

For applying quality control to the code::

    pip install -e .[lint]

* ruff (0.13.3 or later)
* mypy (1.16.0 or later)
* coverage
* pytest (7.2.0 or later)
* pytest-mock
* blackdoc

docs
^^^^

For building documentation::

    pip install -e .[docs]

* sphinx
* sphinx_rtd_theme
* sphinx-toolbox
* nbsphinx
* myst-parser
* blackdoc
* ipython
* pickleshare
* ruff (0.13.3 or later)
* blackdoc
