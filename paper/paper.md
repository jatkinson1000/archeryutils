---
title: "archeryutils: a Python package for archery calculations"
tags:
  - Python
  - Sport
  - Archery
authors:
  - name: Jack Atkinson
    orcid: 0000-0001-5001-4812
    affiliation: 1,2
    corresponding: true
  - name: Thomas Hall
    orcid: 0000-0003-1689-6676
    affiliation: 1
  - name: Liam Patinson
    orcid: 0000-0001-8604-6904
    affiliation: 3
affiliations:
  - name: Archery GB, UK
    index: 1
  - name: Institute of Computing for Climate Science, University of Cambridge, UK
    index: 2
  - name: University of York, UK
    index: 3
date: 26 April 2025
bibliography: paper.bib

---

# Summary

The sport of archery lends itself well to mathematical analysis and indeed there
are several approaches to modelling performance across
different distances and target types.

_archeryutils_ is a Python package that provides base types and functions
for developing code with archery applications, as well as implementations of popular
mathematical models used in the sport.

It is used in multiple applications including the development of websites
and apps for archers, conducting performance analysis for elite archers and governing
bodies, and in ongoing sports science research.


# Statement of Need

In the sport of archery athletes shoot targets at a variety of distances.
Further, these targets can be of different sizes and have different scoring systems
associated with them.
The overall goal is always the same, however; to shoot arrows as accurately and
precisely as possible.
For the purposes of analysis, it is therefore useful to be able to extract some comparative
measure of performance across all targets and distances.
As a precision-based sport, archery lends itself well to mathematical
modelling with examples in literature being @lane2013construction, @park2014modelling, and the
2023 handicap system by Archery GB [@handicaps].
Although these models are well described in their respective papers, no software
implementations have been made publicly available, presenting a barrier to further
research and development.
_archeryutils_ has been developed as a tool to remove this barrier and improve
reproducibility.

Archery score data is increasingly
readily available in electronic formats, be it from competition results
(e.g. on [ianseo](https://ianseo.net/), [tamlynscore](https://www.tamlynscore.co.uk/), etc.)
or the various scoring applications used by archers of all levels.
The _archeryutils_ API is easily combined with Python
data-processing packages, for example
pandas [@The_pandas_development_team_pandas-dev_pandas_Pandas; @mckinney2011pandas] or polars [@polars],
enabling users to perform analysis on these datasets
without needing to reimplement models themselves.


# Software Description

_archeryutils_ is a Python package distributed through the
[Python Package Index (PyPI)](https://pypi.org/project/archeryutils/) with full documentation,
including the API, provided online at
[archeryutils.readthedocs.io](https://archeryutils.readthedocs.io/)

At the core of _archeryutils_ are classes representing the core components of
the sport.
Perhaps the most notable of these are the `Target`, providing a representation
of a target of a particular size, distance, and face type, and the
`Round`, which builds upon this to represent of a series of targets shot at with a
number of arrows.
As well as a constructors for creating generic targets and rounds, _archeryutils_ comes
with many popular national and international rounds predefined for users.
These components provide a starting point for a variety of applications.

The implementation of the mathematical models for precision can be found in the `handicaps`
module.
Available models include both Archery GB handicap schemes of @lane2013construction
and the updated 2023 model and both Archery Australia models of @park2014modelling,
all streamlined into a common API.
There is also the option for users to define custom models by
building on the abstract base class provided.

One other notable component of _archeryutils_ is the `classifications` module.
This provides an implementation of the [Archery GB classification progression
schemes](https://archerygb.org/resources/outdoor-classifications-and-handicaps)
in which archers are categorised and rewarded for their
performance depending on their age, gender, and bowstyle
across the target indoor, target outdoor, and field disciplines.
_archeryutils_ was used to develop these schemes and generate the associated data,
so can be regarded as the definitive source.


# Theory - Precision Models

Whilst specific implementations vary, models for an archer's precision (also called
'handicap' or 'skill level' in literature) take following form:

$$ \sigma_{\theta} (h, d) = \theta (h) \cdot g(d) $$

where $h$ is a number quantifying the archer's handicap
or skill and $\theta(h)$ is a function that relates $h$ to the angular deviation
of their shots.
This can then be mapped downrange to the target at distance $d$, with $g(d)$
quantifying the effect of 'excess dispersion'.^[How angular deviation
grows in excess of a linear relation to distance]

The angular deviation of arrows can be converted into a radial distribution of
on the target face by multiplying by the distance to the target:

$$ \sigma_{r}(h, d) = \sigma_{\theta}(h, d) \cdot d $$

This defines a normal distribution for probability density of where an archer's arrows
will land on the target which can then be integrated with a function for scoring to
get an expected score.

\begin{figure}
    \centering
    \includegraphics[width=\textwidth]{schematic.png}
    \caption{Schematic showing key components of models.}
\end{figure}

These models make key assumptions that the archer is always accurate (dispersed about the centre of the target) and that the archer's arrows are normally distributed with a single value of $\sigma_{\theta}$ (no systematic errors).

The earliest such model is discussed in a series of articles
[@lane1979handicap; @lane1979variation] with equations made available in
@lane2013construction.
It was used to construct the original handicapping scheme of Archery GB, the
national governing body of archery in the United Kingdom.
An alternative model proposed by @park2014modelling is used by Archery Australia,
and forms the basis of their national ranking system.
It has also been applied in studies of competition performance and equipment
[@park2023using; @park2021relative].


# Examples of Use

_archeryutils_ is used in a range of applications.
Its origins lie in the development of the 2023 handicap model for Archery GB where it
was used in conjunction with competition data to develop and tune model parameters
[@handicaps].
It was subsequently used in the development of new Archery GB classification systems
[@outdoor_classifications; @indoor_classifications; @field_classifications].
The software provides the backend for the community website
[archerycalculator](https://archerycalculator.co.uk/), as well as being used in
several other applications and websites.

The models implemented by _archeryutils_ have previously been used in comparative
analyses of athletes' performance and equipment, and there is ongoing research in
this area that uses the software.


# Acknowledgments

JA wishes to thank M Roberts and L Pattinson for helpful discussions whilst developing
algorithms and the early versions of this code.


# References
