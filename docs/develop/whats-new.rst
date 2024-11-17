What's New
==========

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
