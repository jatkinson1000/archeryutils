.. _installing:

Installation
============

Required dependencies
---------------------

- Python (3.10 or later)
- `numpy <https://www.numpy.org/>`__ (1.20 or later)

.. _optional-dependencies:

Installation Instructions
-------------------------

archeryutils is a pure python package.
It can be installed using pip by executing::

    python -m pip install git+https://github.com/jatkinson1000/archeryutils.git

Development Installation
------------------------

To install as a developer you should clone the repository from the online repo and
install as an editable package::

    git clone git@github.com:jatkinson1000/archeryutils.git
    cd archeryutils
    pip install -e .

Testing
~~~~~~~

To run tests on a development installation either install
`pytest <https://docs.pytest.org/>`__ using pip, or install as an optional dependency::

    pip install -e ".[test]"

and then run::

    pytest ./

from within the base directory.

Optional dependencies
~~~~~~~~~~~~~~~~~~~~~

In a similar way to pytest above, there are other optional dependencies that can be
installed with archeryutils:

lint
^^^^

For applying quality control to the code::

    pip install -e ".[lint]"

* black (24.1.0 or later)
* jupyter-black
* pylint
* mypy (1.0.0 or later)
* coverage
* pytest (7.2.0 or later)
* pytest-mock
* pydocstyle

docs
^^^^

For building documentation::

    pip install -e ".[docs]"

* sphinx
* sphinx_rtd_theme
* sphinx-toolbox
* nbsphinx
* blackdoc
* ipython
