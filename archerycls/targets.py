# Author        : Jack Atkinson
#
# Contributors  : Jack Atkinson
#
# Date Created  : 2022-08-16
# Last Modified : 2022-08-16 by Jack Atkinson
#
# Summary       : definition of a target class for archery applications
#
class Target:
    """
    A class used to represent a target face

    Attributes
    ----------
    diameter : float
        Target face diameter in [centimetres]
    distance : float
        Linear distance from archer to target
    scoring_system : str
        the type of target face (scoring system) used

    Methods
    -------
    """
    def __init__(self, diameter, scoring_system, distance=None):
        """
        Parameters
        ----------
        diameter : float
            face diameter in [metres]
        scoring_system : str
            target face/scoring system type
        distance : float
            linear distance from archer to target

        """
        systems = ['5_zone', '10_zone', '10_zone_compound',
                   '10_zone_6_ring', '10_zone_6_ring_compound',
                   '10_zone_5_ring', '10_zone_5_ring_compound',
                   'WA_field',
                   'IFAA_field', 'IFAA_field_expert',
                   'Beiter_hit_miss',
                   'Worcester', 'Worcester_2_ring']

        if scoring_system not in systems:
            raise ValueError("Invalid Target Face Type specified.\n"
                             "Please select from '{}'.".format("', '".join(systems)))

        self.diameter = diameter
        self.distance = distance
        self.sys = scoring_system
