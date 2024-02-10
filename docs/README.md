# archeryutils Documentation

The documentation for archeryutils is written in restructures text and can be build
using sphinx.

To build from this directory run:
```bash
pip install sphinx
make clean
make html
```

The documentation pages can then be viewed in the `_build/html/` directory, with
index.html being the main landing page.

```
docs
 |
 |-- index.rst
 |
 |-- getting-started
 |    |
 |    |-- index.rst
 |    |-- installation.rst
 |    |-- quickstart.rst
 |
 |-- api
 |    |
 |    |-- index.rst
 |    |-- archeryutils.handicaps.rst
 |    |-- archeryutils.classifications.rst
 |
 |-- develop
 |    |
 |    |-- index.rst
 |    |-- contributing.rst
 |    |-- contributors.rst
 |    |-- whats-new.rst
 |
 |-- community
 |    |
 |    |-- index.rst


```
