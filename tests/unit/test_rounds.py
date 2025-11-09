"""Tests for Pass and Round classes."""

import re
from typing import Iterable

import pytest

from archeryutils.rounds import Pass, Round, Target
from archeryutils.targets import ScoringSystem

_target = Target("5_zone", 122, 50)


class TestPass:
    """Tests for the Pass class."""

    def test_init(self) -> None:
        """Check direct initialisation of a Pass with a target instance."""
        test_pass = Pass(36, _target)

        assert test_pass.target == _target
        assert test_pass.n_arrows == 36

    def test_invalid_target(self) -> None:
        """Check that Pass raises a TypeError for invalid target."""
        with pytest.raises(
            TypeError,
            match=re.escape("The target passed to a Pass should be of type Target."),
        ):
            Pass(36, 42)  # type: ignore[arg-type]

    def test_at_target_constructor(self) -> None:
        """Check indirect initialisation of a Pass with target parameters."""
        test_pass = Pass.at_target(36, "5_zone", 122, 50)

        assert test_pass.n_arrows == 36
        assert test_pass.target == _target

    def test_repr(self) -> None:
        """Check Pass string representation."""
        test_pass = Pass(36, _target)
        expected = (
            "Pass(36, Target('5_zone', (122, 'cm'), (50, 'metre'), indoor=False))"
        )
        assert repr(test_pass) == expected

    @pytest.mark.parametrize(
        "other,result",
        [
            pytest.param(
                Pass.at_target(30, "10_zone", 40, (20, "yard")),
                True,
                id="duplicate",
            ),
            pytest.param(
                Pass.at_target(40, "10_zone", 40, (20, "yard")),
                False,
                id="different_arrows",
            ),
            pytest.param(
                Pass.at_target(30, "5_zone", 40, (20, "yard")),
                False,
                id="different_target",
            ),
            pytest.param((30, "10_zone", 40, (20, "yard")), False, id="other_object"),
        ],
    )
    def test_equality(self, other, result) -> None:
        """Check Pass equality comparison is supported."""
        pass_ = Pass.at_target(30, "10_zone", 40, (20, "yard"))

        comparison = pass_ == other
        assert comparison == result

    def test_hash_consistency(self) -> None:
        """Check hash is same for same object."""
        pass_ = Pass.at_target(30, "10_zone", 40, (20, "yard"))

        assert hash(pass_) == hash(pass_)

    def test_hash_uniqueness(self) -> None:
        """Check hash is different for different objects."""
        pass1 = Pass.at_target(30, "10_zone", 40, (20, "yard"))
        pass2 = Pass.at_target(12, "10_zone", 40, (20, "yard"))
        pass3 = Pass.at_target(30, "5_zone", 40, (20, "yard"))
        pass4 = Pass.at_target(30, "10_zone", 122, (20, "yard"))
        pass5 = Pass.at_target(30, "10_zone", 40, (80, "yard"))
        pass6 = Pass.at_target(30, "10_zone", 40, (20, "metre"))

        assert hash(pass1) != hash(pass2)
        assert hash(pass1) != hash(pass3)
        assert hash(pass1) != hash(pass4)
        assert hash(pass1) != hash(pass5)
        assert hash(pass1) != hash(pass6)

    def test_hashable_in_set(self) -> None:
        """Check hash can be used in a set."""
        pass1 = Pass.at_target(30, "10_zone", 40, (20, "yard"))
        pass2 = Pass.at_target(30, "10_zone", 40, (80, "yard"))

        passes_set = {pass1, pass2}
        assert pass1 in passes_set
        assert pass2 in passes_set

    def test_hashable_in_dict(self) -> None:
        """Check hash can be used in a dict as keys."""
        pass1 = Pass.at_target(30, "10_zone", 40, (20, "yard"))
        pass2 = Pass.at_target(30, "10_zone", 40, (80, "yard"))

        rounds_dict = {pass1: "First Pass", pass2: "Second Pass"}
        assert rounds_dict[pass1] == "First Pass"
        assert rounds_dict[pass2] == "Second Pass"

    def test_default_distance_unit(self) -> None:
        """Check that Pass returns distance in metres when units not specified."""
        test_pass = Pass.at_target(36, "5_zone", 122, 50)
        assert test_pass.native_distance.units == "metre"

    def test_default_diameter_unit(self) -> None:
        """Check that Pass has same default diameter units as Target."""
        test_pass = Pass.at_target(36, "5_zone", 122, 50)
        assert (
            test_pass.native_diameter.units
            == test_pass.target.native_diameter.units
            == "cm"
        )

    def test_diameter_units_passed_to_target(self) -> None:
        """Check that Pass passes on diameter units to Target object."""
        test_pass = Pass.at_target(60, "Worcester", (16, "inches"), (20, "yards"))
        assert test_pass.target.native_diameter.units == "inch"

    def test_default_location(self) -> None:
        """Check that Pass returns indoor=False when indoor not specified."""
        test_pass = Pass.at_target(36, "5_zone", 122, 50)
        assert test_pass.indoor is False

    def test_negative_arrows(self) -> None:
        """Check that Pass() uses abs(narrows)."""
        test_pass = Pass(-36, _target)
        assert test_pass.n_arrows == 36

    def test_properties(self) -> None:
        """Check that Pass properties are set correctly."""
        test_pass = Pass(36, Target("5_zone", (122, "cm"), (50, "metre"), False))
        assert test_pass.distance == 50.0
        assert test_pass.native_distance == (50, "metre")
        assert test_pass.diameter == 1.22
        assert test_pass.scoring_system == "5_zone"
        assert test_pass.indoor is False
        assert test_pass.native_diameter == (122, "cm")

    def test_custom_target(self) -> None:
        """Check that pass can be constructed from a custom target specification."""
        target = Target.from_face_spec({0.1: 3, 0.5: 1}, 80, (50, "yard"))
        test_pass = Pass(30, target)
        assert test_pass

    @pytest.mark.parametrize(
        "face_type,max_score_expected",
        [
            ("5_zone", 900),
            ("10_zone", 1000),
            ("11_zone", 1100),
            ("WA_field", 600),
            ("IFAA_field", 500),
            ("AA_national_field", 500),
            ("Worcester_2_ring", 500),
            ("Beiter_hit_miss", 100),
        ],
    )
    def test_max_score(
        self,
        face_type: ScoringSystem,
        max_score_expected: float,
    ) -> None:
        """Check that Pass.max_score() method is functioning correctly."""
        test_pass = Pass.at_target(100, face_type, 122, 50, False)
        assert test_pass.max_score() == max_score_expected


class TestRound:
    """Tests for the Round class."""

    def test_init_with_iterable_passes(self) -> None:
        """
        Check that Round can be intialised with a sequence/iterable of Passes.

        Verify by eq comparison of attribute as Round.__eq__ not defined
        """
        pass_a = Pass.at_target(100, "5_zone", 122, 50, False)
        pass_b = Pass.at_target(100, "5_zone", 122, 40, False)

        list_ = Round("List", [pass_a, pass_b])
        tuple_ = Round("Tuple", (pass_a, pass_b))
        iterable_ = Round("iterable", (p for p in (pass_a, pass_b)))

        assert list_.passes == tuple_.passes == iterable_.passes

    @pytest.mark.parametrize(
        "badpass",
        [
            pytest.param([]),
            pytest.param(()),
        ],
    )
    def test_init_with_empty_passes(self, badpass: Iterable) -> None:
        """Check that Round raises a ValueError for empty passes iterable."""
        with pytest.raises(
            ValueError,
            match=re.escape(
                "passes must contain at least one Pass object but none supplied."
            ),
        ):
            Round("My Round Name", badpass)  # type: ignore[arg-type]

    def test_init_with_incorrect_type_passes(self) -> None:
        """Check that Round raises a TypeError for passes not containing Pass."""
        with pytest.raises(
            TypeError,
            match=re.escape(
                "passes in a Round object should be an iterable of Pass objects."
            ),
        ):
            Round("My Round Name", ["a", "b", "c"])  # type: ignore[list-item]

    def test_repr(self) -> None:
        """Check Pass string representation."""
        test_round = Round("Name", [Pass(36, _target)])
        expected = "<Round: 'Name'>"
        assert repr(test_round) == expected

    @pytest.mark.parametrize(
        "name, args, n_passes, result",
        [
            pytest.param("Test", (), 2, True, id="duplicate"),
            pytest.param(
                "Test",
                ("indoor", "AGB", "Bray"),
                2,
                True,
                id="labelled",
            ),
            pytest.param(
                "Other",
                (),
                2,
                False,
                id="different_name",
            ),
            pytest.param(
                "Test",
                (),
                1,
                False,
                id="different_no_passes",
            ),
        ],
    )
    def test_equality(self, name, args, n_passes, result) -> None:
        """
        Check Round equality comparison is supported.

        duplicate: compare true against an exact duplicate
        labelled: compare true against same round with location, body and family set
        different_name: compare false against same round with different name
        different_no_passes: compare false against same round with one less pass
        """
        target = Target("10_zone", 40, (20, "yard"), indoor=True)
        pass_ = Pass(30, target)

        round_ = Round("Test", [pass_, pass_])
        comparison = round_ == Round(name, [pass_] * n_passes, *args)
        assert comparison == result

    def test_equality_pass_order(self) -> None:
        """Check Round equality comparison for alternative pass permutations."""
        target_1 = Target("10_zone", 122, 90)
        target_2 = Target("10_zone", 122, 70)
        pass_1 = Pass(30, target_1)
        pass_2 = Pass(30, target_2)
        round_a = Round("Test", [pass_1, pass_2])
        round_b = Round("Test", [pass_2, pass_1])

        assert round_a != round_b

    def test_equality_different_object(self) -> None:
        """Check Round equality comparison against a differnt type of object."""
        target = Target("10_zone", 40, (20, "yard"), indoor=True)
        pass_ = Pass(30, target)
        round_ = Round("Test", [pass_, pass_])

        assert round_ != ("Test", [pass_, pass_])

    def test_hash_consistency(self) -> None:
        """Check hash is same for same object."""
        target = Target("10_zone", 40, (20, "yard"), indoor=True)
        pass_ = Pass(30, target)
        round_ = Round("Test", [pass_, pass_])

        assert hash(round_) == hash(round_)

    def test_hash_uniqueness(self) -> None:
        """Check hash is different for different objects."""
        target = Target("10_zone", 40, (20, "yard"), indoor=True)
        pass_ = Pass(30, target)
        round1 = Round("Test1", [pass_, pass_])
        round2 = Round("Test2", [pass_, pass_])

        assert hash(round1) != hash(round2)

    def test_hashable_in_set(self) -> None:
        """Check hash can be used in a set."""
        target = Target("10_zone", 40, (20, "yard"), indoor=True)
        pass_ = Pass(30, target)
        round1 = Round("Test1", [pass_, pass_])
        round2 = Round("Test2", [pass_, pass_])

        rounds_set = {round1, round2}
        assert round1 in rounds_set
        assert round2 in rounds_set

    def test_hashable_in_dict(self) -> None:
        """Check hash can be used in a dict as keys."""
        target = Target("10_zone", 40, (20, "yard"), indoor=True)
        pass_ = Pass(30, target)
        round1 = Round("Test1", [pass_, pass_])
        round2 = Round("Test2", [pass_, pass_])

        rounds_dict = {round1: "First Round", round2: "Second Round"}
        assert rounds_dict[round1] == "First Round"
        assert rounds_dict[round2] == "Second Round"

    @pytest.mark.parametrize(
        "passes,result",
        [
            pytest.param(
                [
                    Pass.at_target(100, "5_zone", 122, 50, False),
                    Pass.at_target(100, "5_zone", 122, 40, False),
                    Pass.at_target(100, "5_zone", 122, 30, False),
                ],
                300,
            ),
            pytest.param(
                [
                    Pass.at_target(100, "5_zone", 122, 50, False),
                ],
                100,
            ),
            pytest.param(
                [
                    Pass.at_target(100, "5_zone", 122, 50, False),
                    Pass.at_target(50, "5_zone", 122, 40, False),
                    Pass.at_target(25, "5_zone", 80, 30, False),
                ],
                175,
            ),
        ],
    )
    def test_n_arrows(self, passes: Iterable, result: int) -> None:
        """Check that n_arrows attribute is calculated correctly for a Round."""
        test_round = Round(
            "MyRound",
            passes,
        )
        assert test_round.n_arrows == result

    def test_max_score(self) -> None:
        """Check that max score is calculated correctly for a Round."""
        test_round = Round(
            "MyRound",
            [
                Pass.at_target(100, "5_zone", 122, 50, False),
                Pass.at_target(100, "5_zone", 122, 40, False),
                Pass.at_target(100, "5_zone", 122, 30, False),
            ],
        )
        assert test_round.max_score() == 2700

    @pytest.mark.parametrize(
        "unit,get_unit,max_dist_expected",
        [
            ("metres", True, (100, "metre")),
            ("yards", True, (100, "yard")),
            ("metres", False, 100),
            ("yards", False, 100),
        ],
    )
    def test_max_distance(
        self,
        unit: str,
        get_unit: bool,
        max_dist_expected: float | tuple[float, str],
    ) -> None:
        """
        Check that max distance is calculated correctly for a Round.

        Returns a tuple or float depending on input argument.
        Always returns the distance in appropriate units regardless of whether unit
        requested or not - i.e. should not convert yards to metres.
        """
        test_round = Round(
            "MyRound",
            [
                Pass.at_target(10, "5_zone", 122, (100, unit), False),
                Pass.at_target(10, "5_zone", 122, (80, unit), False),
                Pass.at_target(10, "5_zone", 122, (60, unit), False),
            ],
        )
        result = (
            test_round.max_distance() if get_unit else test_round.max_distance().value
        )
        assert result == max_dist_expected

    def test_max_distance_out_of_order(self) -> None:
        """Check max distance correct when Passes not in descending distance order."""
        test_round = Round(
            "MyRound",
            [
                Pass.at_target(10, "5_zone", 122, 80, False),
                Pass.at_target(10, "5_zone", 122, 100, False),
                Pass.at_target(10, "5_zone", 122, 60, False),
            ],
        )
        assert test_round.max_distance().value == 100

    def test_max_distance_mixed_units(self) -> None:
        """Check that max distance accounts for different units in round."""
        pyards = Pass.at_target(36, "5_zone", 122, (80, "yard"))
        pmetric = Pass.at_target(36, "5_zone", 122, (75, "metres"))
        test_round = Round("test", [pyards, pmetric])

        assert pmetric.distance > pyards.distance
        assert test_round.max_distance().value == 75

    def test_n_arrows(self) -> None:
        """Check that number of arrows is calculated correctly for a Round."""
        test_round = Round(
            "MyRound",
            [
                Pass.at_target(72, "5_zone", 122, 50, False),
                Pass.at_target(48, "5_zone", 122, 40, False),
                Pass.at_target(24, "5_zone", 122, 30, False),
            ],
        )
        assert test_round.n_arrows == 144

    def test_get_info(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Check printing info works as expected."""
        test_round = Round(
            "MyRound",
            [
                Pass.at_target(10, "5_zone", 122, 100, False),
                Pass.at_target(20, "5_zone", 122, (80, "yards"), False),
                Pass.at_target(30, "5_zone", 80, (60, "metre"), False),
            ],
        )
        test_round.get_info()
        captured = capsys.readouterr()
        assert captured.out == (
            "A MyRound consists of 3 passes:\n"
            + "\t- 10 arrows at a 122.0 cm target at 100.0 metres.\n"
            + "\t- 20 arrows at a 122.0 cm target at 80.0 yards.\n"
            + "\t- 30 arrows at a 80.0 cm target at 60.0 metres.\n"
        )
