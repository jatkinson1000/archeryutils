What's New
==========

Latest
------
* Allow inputs to classification functions to be an archeryutils `Round`
  as well as a string in `#119 <https://github.com/jatkinson1000/archeryutils/pull/119>`_
* Add new AGB 900 rounds in `#116 <https://github.com/jatkinson1000/archeryutils/pull/116>`_
* API change to use enums for inputs to classification functions
  in `#113 <https://github.com/jatkinson1000/archeryutils/pull/113>`_
* Adds `n_arrows` attribute to `Round`
  in `#111 <https://github.com/jatkinson1000/archeryutils/pull/111>`_
* Move to use flattened loops in classification dict generation by `@TomHall2020 <https://github.com/TomHall2020>`_
  in `#110 <https://github.com/jatkinson1000/archeryutils/pull/110>`_
* Fixes issue whereby a divide-by-zero warning could arise in the handicap rootfinding algorithm
  in `#109 <https://github.com/jatkinson1000/archeryutils/pull/109>`_
* Bugfix: Field classification naming made consistent with other schemes.
* Dependencies:
  * Latest ruff
  * Use dev mypy from GitHub to resolve bug
  * Pin sphinx at <8.2.0 due to typing incompatibilities


Version 1.1.1
-------------
* Fixes a bug in version 1.1.0 whereby shorter-peg rounds were not restricted to
  the Archer tier in field classifications.
* Tests added to cover this.


Version 1.1.0
-------------
* Updated field classifications to the 2025 Archery GB scheme:

   * Uses new age groups, rounds, classifications and scores
   * For full details see `archerycalculator.co.uk/new-field <https://archerycalculator.co.uk/new-field>`_
   * Added option to use "English Longbow" as a bowstyle alias
   * Old field classifications archived but still available using ``old`` in the function calls. See `related API documentation <https://archeryutils.readthedocs.io/en/latest/api/archeryutils.classifications.html#archeryutils.classifications.old_agb_field_classification_scores>`_

* Test suite extended to cover Python 3.13
* Linting moved to use ruff v0.7.3
* Coverage workflows updated to latest versions


Version 1.0.0
-------------
* Initial release of archeryutils.
