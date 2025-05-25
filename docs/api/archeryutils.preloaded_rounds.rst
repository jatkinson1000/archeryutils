Preloaded Rounds
================

*archeryutils* comes with a number of rounds pre-loaded through the ``load_rounds``
module.
These are stored in a series of dictionaries and can be accessed using the python
dot-notation.

For example, to load all WA Outdoor rounds and then extract the WA1440 (90m) we can do:

.. ipython:: python

    import archeryutils as au

    wa_outdoor_rounds = au.load_rounds.WA_outdoor
    my_wa1440_90 = wa_outdoor_rounds.wa1440_90

    print(my_wa1440_90)

    my_wa1440_90.get_info()

Or, to load the round directly:

.. ipython:: python

    import archeryutils as au

    au.load_rounds.WA_outdoor.wa1440_90

See below for a list of all available round dictionaries, and the rounds they contain.
The keys of the dictionary should be used for dot-notation access.

WA Outdoor
----------

.. ipython:: python

    import archeryutils as au

    au.load_rounds.AGB_outdoor_imperial

AGB (Archery GB) Outdoor Imperial
---------------------------------

.. ipython:: python

    import archeryutils as au

    au.load_rounds.WA_outdoor

AGB (Archery GB) Outdoor Metric
-------------------------------

.. ipython:: python

    import archeryutils as au

    au.load_rounds.AGB_outdoor_metric

AGB (Archery GB) Outdoor Imperial
---------------------------------

.. ipython:: python

    import archeryutils as au

    au.load_rounds.AGB_outdoor_imperial

WA Indoor
---------

.. ipython:: python

    import archeryutils as au

    au.load_rounds.WA_indoor

AGB (Archery GB) Indoor
-----------------------

.. ipython:: python

    import archeryutils as au

    au.load_rounds.AGB_indoor

WA Field
--------

.. ipython:: python

    import archeryutils as au

    au.load_rounds.WA_field

IFAA Field
----------

.. ipython:: python

    import archeryutils as au

    au.load_rounds.IFAA_field

WA VI
-----

.. ipython:: python

    import archeryutils as au

    au.load_rounds.WA_VI

AGB (Archery GB) VI
-------------------

.. ipython:: python

    import archeryutils as au

    au.load_rounds.AGB_VI

AA (Archery Australia) Outdoor
------------------------------

.. ipython:: python

    import archeryutils as au

    au.load_rounds.AA_outdoor_metric

AA (Archery Australia) Indoor
-----------------------------

.. ipython:: python

    import archeryutils as au

    au.load_rounds.AA_indoor

AA (Archery Australia) Field
----------------------------

.. ipython:: python

    import archeryutils as au

    au.load_rounds.AA_field

Miscellaneous
-------------

.. ipython:: python

    import archeryutils as au

    au.load_rounds.misc
