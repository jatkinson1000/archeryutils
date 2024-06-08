# archeryutils

[![PyPI - Version](https://img.shields.io/pypi/v/archeryutils)](https://pypi.org/project/archeryutils)
![GitHub](https://img.shields.io/github/license/jatkinson1000/archeryutils)
[![Documentation Status](https://readthedocs.org/projects/archeryutils/badge/?version=latest)](https://archeryutils.readthedocs.io/en/latest/?badge=latest)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/jatkinson1000/archeryutils/testing.yaml)
[![codecov](https://codecov.io/gh/jatkinson1000/archeryutils/branch/main/graph/badge.svg?token=AZU7G6H8T0)](https://codecov.io/gh/jatkinson1000/archeryutils)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/jatkinson1000/archeryutils/main?labpath=examples.ipynb)

A collection of archery code and utilities in python.\
Designed to make the development of archery codes and apps easier.

Contains:
- generic representations of targets and rounds
- World Archery, Archery GB, IFAA rounds
- calculations for Archery GB handicaps and Archery Australia archer skill level
- calculation of Archery GB classifications

Full documentation, including an API reference, is available on
[read the docs](https://archeryutils.readthedocs.io).


## Try now!
You can play with this library as a
[binder instance](https://mybinder.org/v2/gh/jatkinson1000/archeryutils/main?labpath=examples.ipynb)
right now without installing anything.  
If you want to use it locally in your own code follow the usage instructions below for
[installation](#installation) and getting started.


## Usage
Usage is allowed under the [licensing specified](https://github.com/jatkinson1000/archeryutils#license).
We encourage usage and welcome feature requests.
It is appreciated if visible credit is given by any projects using `archeryutils`.

### Installation
To install the library via pip for use in a project you can run:

    pip install archeryutils

It is recommended to use a virtual environment.

If you want a local install that you can edit instead, clone the repository,
navigate to `archeryutils/`, and run:

    python3 -m pip install -e .[test,lint,docs]

Please refer to the online documentation for
[full installation guidance](https://archeryutils.readthedocs.io/en/latest/getting-started/installation.html).

### Getting Started
There are examples of some of the different functionalities in the jupyter notebook
`examples.ipynb`.
This can be run from a local install using:

    pip install notebook

    jupyter notebook examples.ipynb

Alternatively, you can use it online through the
[binder instance](https://mybinder.org/v2/gh/jatkinson1000/archeryutils/main?labpath=examples.ipynb)
as described above.

### License
Copyright &copy; Jack Atkinson

_archeryutils_ is distributed under the
[MIT Licence](https://github.com/jatkinson1000/archeryutils/blob/main/LICENSE).

### Authors and Acknowledgment
See [Contributors](https://github.com/jatkinson1000/archeryutils/graphs/contributors)
for a full list of contributors towards this project.

If you use this software in your work, please provide visible credit/citation.
[CITATION.cff](https://github.com/jatkinson1000/archeryutils/blob/main/CITATION.cff)
provides citation metadata, which can also be accessed from
[GitHub](https://github.com/jatkinson1000/archeryutils).

### Used by
The following projects make use of this code or derivatives in some way:

- [archerycalculator](https://archerycalculator.co.uk)
- MyTargets
- Golden Records
- Expert Archer

Are we missing anyone? Let us know.

If you make use of *archeryutils* in a commercial product please consider
[supporting](#support) the project to ensure its continued development and longevity.


## Contributions
Contributions and collaborations are welcome from anyone with an
interest in python and archery.

Please refer to the online documentation for full
[contributing guidelines](https://archeryutils.readthedocs.io/en/latest/develop/contributing.html).\
Read and follow this when opening
[issues](https://archeryutils.readthedocs.io/en/latest/develop/contributing.html#bug-reports-and-feature-requests)
or 
[pull requests](https://archeryutils.readthedocs.io/en/latest/develop/contributing.html#code-contributions).

For bugs, feature requests, and clear suggestions for improvement can be documented by
[opening an issue](https://github.com/jatkinson1000/archeryutils/issues).
For more abstract ideas for the project please
[open a discussion](https://github.com/jatkinson1000/archeryutils/discussions).

If you built something upon _archeryutils_ that would be useful to others, or can
address an [open issue](https://github.com/jatkinson1000/archeryutils/issues), please
[fork the repository](https://github.com/jatkinson1000/archeryutils/fork) and open a
pull request.

### Code of Conduct
Everyone participating in the _archeryutils_ project, and in particular in the
issue tracker, pull requests, and social media activity, is expected to treat other
people with respect and more generally to follow the guidelines articulated in the
[Python Community Code of Conduct](https://www.python.org/psf/codeofconduct/).


## Support
This project is developed by volunteers for the benefit of the archery community.
It is dedicated to remain a [FOSS](https://itsfoss.com/what-is-foss/) project.
The best way to support this project, if you are able, is by directly
[contributing](https://github.com/jatkinson1000/archeryutils/tree/project-documentation#contributions).

If you are unable to do this, however, financial support towards this and the
[archerycalculator](https://archerycalculator.co.uk) project can be given through
[Buy me a coffee](https://www.buymeacoffee.com/jackatkinsr) or
[donating via paypal](https://www.paypal.com/donate/?hosted_button_id=JEABJ3UJU4XD4).
This allows me to spend time improving the library.
