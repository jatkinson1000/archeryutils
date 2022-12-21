import numpy as np
import json


class Classification:
    # A class object for holding classification information

    def __init__(
        self,
        name,
        system,
        classes,
        groups,
        handicap_matrix,
    ):
        """
        Parameters
        ----------
        name : str
            name of this classification group e.g. "BowstyleGender"
        system : str
            ID of the handicap system used for these classifications
        classes : list of str
            Names of Classifications (ideally high to low)
        groups : list of str
            Names of Groups e.g. ages
        HC : ndarray
            Array of handicaps for classes and groups (len(groups), len(classes)
        """
        self.name = name
        self.system = system
        self.classes = classes
        self.groups = groups
        self.HC = handicap_matrix

        if np.shape(handicap_matrix) != (len(groups), len(classes)):
            raise IndexError(f"Shape of HC ({np.shape(HC)}) does not match"
                             f"groups ({len(groups)}), and classes ({len(classes)}).")

    def get_handicaps_for_class(self, class_name):
        try:
            i = self.classes.index(class_name)
            return self.HC[:, i]
        except ValueError as e:
            raise Exception(f"'{class_name}' does not appear in the list of classes {self.classes}.") from e

    def get_handicaps_for_group(self, group_name):
        try:
            i = self.groups.index(group_name)
            return self.HC[i, :]
        except ValueError as e:
            raise Exception(f"'{group_name}' does not appear in the list of classes {self.groups}.") from e

    def get_handicap(self, group_name, class_name):
        try:
            i = self.groups.index(group_name)
        except ValueError as e:
            raise Exception(f"'{group_name}' does not appear in the list of classes {self.groups}.") from e
        try:
            j = self.classes.index(class_name)
        except ValueError as e:
            raise Exception(f"'{class_name}' does not appear in the list of classes {self.classes}.") from e
        return self.HC[i, j]

    @classmethod
    def make_agb_table(cls, name, class_step, group_step, datum):
        system = "AGB"
        classes = ["SMB", "GMB", "MB", "B1", "B2", "B3", "A1", "A2", "A3"]
        groups = ["50+", "Sen", "U21", "U18", "U16", "U14", "U12"]
        HC = np.empty([len(groups), len(classes)])
        # Senior MB is datum value, set relative to this
        HC[1, 2] = datum
        # Set MB for all groups
        HC[1:, 2] = HC[1, 2] + np.arange(len(groups)-1) * group_step
        HC[0, 2] = HC[1, 2] + group_step
        # Set other classes for all groups
        HC[:, :] = (np.tile(HC[:, 2], (len(classes), 1)).T
                    + np.arange(-2, len(classes) - 2) * class_step * np.ones([len(groups), len(classes)]))

        return cls(name, system, classes, groups, HC)


if __name__ == "__main__":

    RM = Classification.make_agb_table("RM", 7, 7, 30)
    RW = Classification.make_agb_table("RW", 7, 7, 37)
    CM = Classification.make_agb_table("CM", 7, 5, 17)

    print(RM.get_handicap("U18", "B2"))
    print(RW.get_handicap("U18", "B2"))
    print(CM.get_handicap("U18", "B2"))

