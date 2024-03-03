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

AGB Outdoor Imperial
--------------------

.. ipython:: python

    import archeryutils as au
    au.load_rounds.WA_outdoor

AGB Outdoor Metric
--------------------

.. ipython:: python

    import archeryutils as au
    au.load_rounds.AGB_outdoor_metric

AGB Outdoor Imperial
--------------------

.. ipython:: python

    import archeryutils as au
    au.load_rounds.AGB_outdoor_imperial

WA Indoor
---------

.. ipython:: python

    import archeryutils as au
    au.load_rounds.WA_indoor

AGB Indoor
----------

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

AGB VI
------

.. ipython:: python

    import archeryutils as au
    au.load_rounds.AGB_VI

Custom Rounds
-------------

.. ipython:: python

    import archeryutils as au
    au.load_rounds.custom
