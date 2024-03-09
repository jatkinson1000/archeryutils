.. _quickstart:

Quick-Start Guide
=================

This page contains a few quick examples of how you can use archeryutils.
For full details and functionalities you should consult the rest of the documentation.

Examples Notebook
-----------------

The `source repository <https://github.com/jatkinson1000/archeryutils>`__ contains
`a notebook of examples <https://github.com/jatkinson1000/archeryutils/blob/main/examples.ipynb>`__ `exercises.ipynb`
which is very similar to the examples on this page.
This is the perfect place to learn the basic functionalities of archeryutils and
experiment yourself with what the code can do. 
We advise starting by running this.

To do so online you can access the
`Binder instance <https://mybinder.org/v2/gh/jatkinson1000/archeryutils/main?labpath=examples.ipynb>`__
we have set up.
This will spin up an interactive online session in which you can run the code.

Alternatively you can run it locally in your browser by downloading the notebook and
running::

    pip install jupyter
    jupyter notebook examples.ipynb


Importing
---------

To import the archeryutils package use:

.. ipython:: python

    import archeryutils as au

Target
------

The most basic building block of archeryutils is the :py:class:`archeryutils.Target`
class which represents a target with a particular target face at a certain distance.

It can be invoked by specifying a scoring system, face size (cm) and distance (m):

.. ipython:: python

    my720target = au.Target("10_zone", 122, 70.0)
    mycompound720target = au.Target("10_zone_6_ring", 80, 50.0)

In more complicated cases specific units can be passed in with the diameter and distance
as a tuple:

.. ipython:: python

    myWorcesterTarget = au.Target(
        "Worcester", diameter=(16, "inches"), distance=(20.0, "yards"), indoor=True
    )
    myIFAATarget = au.Target("IFAA_field", diameter=80, distance=(80.0, "yards"))

If the target you want is not supported, you can manually supply the target ring sizes
and scores as a `FaceSpec` and construct a target as so.

.. ipython:: python

    # Kings of archery recurve scoring target
    face_spec = {8: 10, 12: 8, 16: 7, 20: 6}
    myKingsTarget = au.Target.from_face_spec((face_spec, "cm"), 40, 18, indoor=True)
    print(myKingsTarget.scoring_system)

.. note::
    Although we can provide the face_spec in any unit listed under :py:attr:`~archeryutils.Target.supported_diameter_units`,
    the sizes in the specification are converted to metres and stored in this form.
    Therefore unlike the target diameter paramater, the default unit for specifications is [metres]

The only limitations to the target faces you can represent in this way are:

1. Targets must be formed of concentric rings
2. The score must monotonically decrease as the rings get larger

Under the hood, all standard scoring systems autogenerate their own `FaceSpec` and this is used
internally when calculating handicaps and classifications. You can see this stored under the
:py:attr:`~archeryutils.Target.face_spec` property:

.. ipython:: python

    print(my720target.face_spec)

The target features `max_score()` and `min_score()` methods:

.. ipython:: python

    for target in [
        my720target,
        mycompound720target,
        myIFAATarget,
        myWorcesterTarget,
        myKingsTarget,
    ]:
        print(
            f"{target.scoring_system} has max score {target.max_score()} ",
            f"and min score {target.min_score()}.",
        )

Pass
----

The next unit up is the :py:class:`archeryutils.Pass` - a number of arrows shot at
a target:

.. ipython:: python

    my70mPass = au.Pass(36, my720target)
    print(my70mPass.max_score())

We can also bypass the Target class and directly construct our Pass using the `at_target` constructor

.. ipython:: python

    my70mPass = au.Pass.at_target(36, "10_zone", 122, 70.0)

Round
-----

Finally we have the :py:class:`archeryutils.Round` class made up of a number of Passes.

It may also take the following optional string arguments:

* ``location`` - where the round is shot, e.g. 'Indoor', 'Outdoor', 'Field' etc.
* ``body`` - The governing body the round is defined by, e.g. 'WA', 'IFAA', 'AGB', 'AA' etc.
* ``family`` - The larger family of rounds to which this round belongs, e.g. 'WA1440', 'WA720', 'Nationals' etc.


.. ipython:: python

    my720Round = au.Round(
        "WA 720 (70m)",
        [my70mPass, my70mPass],
        location="Outdoor Target",
        body="WA",
        family="WA720",
    )

Default Rounds
--------------

A number of useful rounds are pre-defined and come preloaded as dictionaries that can be imported:

.. ipython:: python

    from archeryutils import load_rounds

    agb_outdoor = load_rounds.AGB_outdoor_imperial

    for round_i in agb_outdoor.values():
        print(round_i.name)

Individial rounds are accessible via 'dot' notation (using the alias listed in agb_outdoor.keys()) as follows:

.. ipython:: python

    agb_outdoor.york.get_info()

    agb_outdoor.york.max_score()

Possible options for round collections are:

* ``AGB_outdoor_imperial`` - Archery GB outdoor imperial rounds
* ``AGB_outdoor_metric`` - Archery GB outdoor metric rounds
* ``AGB_indoor`` - Archery GB indoor rounds
* ``WA_outdoor`` - World Archery outdoor rounds
* ``WA_indoor`` - World Archery indoor rounds
* ``WA_field`` - World Archery field rounds
* ``IFAA_field`` - IFAA indoor and outdoor rounds
* ``AGB_VI`` - Archery GB Visually Impaired rounds
* ``WA_VI`` - World Archery Visually Impaired rounds
* ``misc`` - Miscellaneous rounds such as individual distances, 252 awards, frostbites etc.

Handicap Schemes
----------------

archeryutils features support for calculations using a number of different handicap
schemes for accuracy measurement, including those of
Archery GB (Atkinson (2023), Lane (1978)) and Archery Australia (Park (2014)).

.. ipython:: python

    from archeryutils import handicaps as hc

Given a handicap and a round we can calculate the score that would be achieved:

.. ipython:: python

    score_from_hc = hc.score_for_round(
        38,
        agb_outdoor.york,
        "AGB",
    )

    print(f"A handicap of 38 on a York is a score of {score_from_hc}.")

    pass_scores = hc.score_for_passes(
        38,
        agb_outdoor.york,
        "AGB",
    )

    print(f"A handicap of 38 on a York gives pass scores of {pass_scores}.")

Perhaps more interestingly we can take a score on a particular round and convert it
to a handicap:

.. ipython:: python

    hc_from_score = hc.handicap_from_score(
        950,
        agb_outdoor.york,
        "AGB",
    )
    print(f"A score of 950 on a York is a continuous handicap of {hc_from_score}.")

    hc_from_score = hc.handicap_from_score(
        950,
        agb_outdoor.york,
        "AGB",
        int_prec=True,
    )
    print(f"A score of 950 on a York is a discrete handicap of {hc_from_score}.")

There is also the HandicapTable class for generating handicap tables:

.. ipython:: python

    handicaps = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    rounds = [
        agb_outdoor.york,
        agb_outdoor.hereford,
        agb_outdoor.st_george,
        agb_outdoor.albion,
    ]
    # The following would allow printing of handicap tables for an entire group of rounds:
    # rounds = list(load_rounds.AGB_outdoor_imperial.values())

    my_agb_table = hc.HandicapTable(
        "AGB",
        handicaps,
        rounds,
    )
    my_agb_table.print()


Classifications
---------------

Finally there is support for the various Archery GB classification schemes

For full details see the summary on
`archerycalculator.com <https://archerycalculator.co.uk/info>`_, the Archery GB website
`here <https://archerygb.org/resources/outdoor-classifications-and-handicaps>`_
and `here <https://archerygb.org/resources/indoor-classifications-and-handicaps>`_,
and the Shooting Administrative Procedures.

Given a score we can calculate the classification it achieves:

.. ipython:: python

    from archeryutils import classifications as class_func

    # AGB Outdoor
    class_from_score = class_func.calculate_agb_outdoor_classification(
        965,
        "hereford",
        "recurve",
        "male",
        "50+",
    )
    print(
        f"A score of 965 on a Hereford is class {class_from_score} for a 50+ male recurve."
    )

    # AGB Indoor
    class_from_score = class_func.calculate_agb_indoor_classification(
        562,
        "wa18",
        "compound",
        "female",
        "adult",
    )
    print(
        f"A score of 562 on a WA 18 is class {class_from_score} for adult female compound."
    )

    # AGB Field
    class_from_score = class_func.calculate_agb_field_classification(
        168,
        "wa_field_24_blue_unmarked",
        "traditional",
        "male",
        "under 18",
    )
    print(
        f"A score of 168 on a WA Unmarked 24 is class {class_from_score} for an under 18 male traditional."
    )

Or, given a round we can output the scores required for each classification band:

.. ipython:: python

    class_scores = class_func.agb_outdoor_classification_scores(
        "hereford",
        "recurve",
        "male",
        "adult",
    )
    print(class_scores)

    class_scores = class_func.agb_indoor_classification_scores(
        "portsmouth",
        "compound",
        "female",
        "adult",
    )
    print(class_scores)

    class_scores = class_func.agb_field_classification_scores(
        "wa_field_24_blue_marked",
        "flatbow",
        "female",
        "under 18",
    )
    print(class_scores)



