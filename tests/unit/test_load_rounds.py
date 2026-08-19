"""Tests for round loading and DotDict deprecation behaviour."""

import warnings
from typing import Any

import pytest

from archeryutils import Pass, load_rounds
from archeryutils.load_rounds import DotDict, _collect_deprecated_names
from archeryutils.rounds import Round


def _round(codename: str) -> Round:
    """Build a minimal Round for test fixtures."""
    return Round(
        codename,
        [Pass.at_target(36, "10_zone", 122, 70.0)],
        codename=codename,
    )


def _round_entry(
    codename: str,
    deprecated_names: list[str] | None = None,
) -> dict[str, Any]:
    """Build a minimal round data entry for test fixtures."""
    entry: dict[str, Any] = {
        "name": codename,
        "codename": codename,
        "location": "outdoor",
        "body": "AGB",
        "family": "test",
        "passes": [],
    }
    if deprecated_names is not None:
        entry["deprecated_names"] = deprecated_names
    return entry


class TestDotDictDeprecatedNames:
    """Tests for backwards-compatible deprecation resolution on DotDict."""

    @pytest.fixture
    def rounds(self) -> DotDict[Round]:
        """Return a DotDict with two rounds and deprecated names for one."""
        return DotDict(
            {"new_name": _round("new_name"), "other": _round("other")},
            deprecated_names={"old_name": "new_name", "older_name": "new_name"},
        )

    def test_canonical_lookup_no_warning(self, rounds: DotDict[Round]) -> None:
        """Canonical codenames look up without any deprecation warning."""
        with warnings.catch_warnings():
            warnings.simplefilter("error", DeprecationWarning)
            assert isinstance(rounds["new_name"], Round)

    def test_deprecated_lookup_returns_canonical_and_warns(
        self, rounds: DotDict[Round]
    ) -> None:
        """A deprecated codename resolves to the canonical Round with a warning."""
        with pytest.warns(DeprecationWarning, match=r"'old_name'.*'new_name'"):
            value = rounds["old_name"]
        assert value is rounds["new_name"]

    def test_deprecated_membership_no_warning(self, rounds: DotDict[Round]) -> None:
        """Membership tests recognise deprecated names but do not emit a warning."""
        with warnings.catch_warnings():
            warnings.simplefilter("error", DeprecationWarning)
            assert "old_name" in rounds
            assert "missing" not in rounds

    def test_deprecated_get_warns_and_resolves(self, rounds: DotDict[Round]) -> None:
        """``get`` resolves deprecated names and warns, like ``__getitem__``."""
        with pytest.warns(DeprecationWarning, match=r"'older_name'.*'new_name'"):
            value = rounds.get("older_name")
        assert value is rounds["new_name"]

    def test_get_missing_returns_default(self, rounds: DotDict[Round]) -> None:
        """``get`` on an unknown codename returns the default without warning."""
        with warnings.catch_warnings():
            warnings.simplefilter("error", DeprecationWarning)
            assert rounds.get("missing", "default") == "default"

    def test_keys_exclude_deprecated_names(self, rounds: DotDict[Round]) -> None:
        """Deprecated names never appear in keys()/values()/items()."""
        keys = list(rounds.keys())
        assert "new_name" in keys
        assert "old_name" not in keys
        assert len(list(rounds.values())) == 2
        assert len(list(rounds.items())) == 2

    def test_dot_access_deprecated_warns(self, rounds: DotDict[Round]) -> None:
        """Dot-notation access of a deprecated name warns and returns canonical."""
        with pytest.warns(DeprecationWarning):
            assert rounds.old_name is rounds["new_name"]

    def test_dot_access_canonical_no_warning(self, rounds: DotDict[Round]) -> None:
        """Dot-notation access of a canonical codename does not warn."""
        with warnings.catch_warnings():
            warnings.simplefilter("error", DeprecationWarning)
            assert isinstance(rounds.new_name, Round)

    def test_missing_key_raises_keyerror(self, rounds: DotDict[Round]) -> None:
        """Looking up an unknown codename raises KeyError."""
        with pytest.raises(KeyError):
            rounds["missing"]

    def test_missing_attribute_raises_attributeerror(
        self, rounds: DotDict[Round]
    ) -> None:
        """Dot-notation access of an unknown name raises AttributeError."""
        with pytest.raises(AttributeError):
            _ = rounds.nonexistent

    def test_setattr_adds_item(self, rounds: DotDict[Round]) -> None:
        """Setting an attribute via dot notation inserts it as a dict item."""
        extra = _round("extra")
        rounds.extra = extra
        assert rounds["extra"] is extra
        assert "extra" in rounds

    def test_delattr_removes_item(self, rounds: DotDict[Round]) -> None:
        """Deleting an attribute via dot notation removes it from the dict."""
        assert "other" in rounds
        del rounds.other
        assert "other" not in rounds

    def test_delattr_missing_raises_attributeerror(
        self, rounds: DotDict[Round]
    ) -> None:
        """Deleting an unknown attribute via dot notation raises AttributeError."""
        with pytest.raises(AttributeError):
            del rounds.nonexistent

    def test_codename_attribute_is_canonical(self, rounds: DotDict[Round]) -> None:
        """The Round returned via a deprecation reports the canonical codename."""
        with pytest.warns(DeprecationWarning):
            assert rounds["old_name"].codename == "new_name"

    def test_no_deprecated_names_kwarg(self) -> None:
        """DotDict constructed without deprecated names is a plain dict."""
        dd: DotDict[Round] = DotDict({"a": _round("a")})
        assert "a" in dd
        assert "b" not in dd
        with pytest.raises(KeyError):
            dd["b"]


class TestCollectDeprecatedNames:
    """Tests for _collect_deprecated_names validation logic."""

    def test_no_deprecated_names_returns_empty(self) -> None:
        """Rounds without a 'deprecated_names' field give an empty mapping."""
        assert _collect_deprecated_names([_round_entry("a"), _round_entry("b")]) == {}

    def test_collects_deprecated_names(self) -> None:
        """Deprecated names are collected into a mapping."""
        data = [_round_entry("new", deprecated_names=["old", "older"])]
        assert _collect_deprecated_names(data) == {"old": "new", "older": "new"}

    def test_clash_with_codename_raises(self) -> None:
        """A deprecated name matching a canonical codename is rejected."""
        data = [_round_entry("a", deprecated_names=["b"]), _round_entry("b")]
        with pytest.raises(ValueError, match="clashes"):
            _collect_deprecated_names(data)

    def test_duplicate_deprecated_name_raises(self) -> None:
        """The same deprecated name declared by two rounds is rejected."""
        data = [
            _round_entry("a", deprecated_names=["dup"]),
            _round_entry("b", deprecated_names=["dup"]),
        ]
        with pytest.raises(ValueError, match=r"Duplicate deprecated codename 'dup'"):
            _collect_deprecated_names(data)


class TestDotDictAdd:
    """Tests for combining DotDicts with ``+``."""

    @pytest.fixture
    def left(self) -> DotDict[Round]:
        """Return a DotDict with two rounds and a deprecated name."""
        return DotDict(
            {"a": _round("a"), "b": _round("b")},
            deprecated_names={"old_a": "a"},
        )

    @pytest.fixture
    def right(self) -> DotDict[Round]:
        """Return a DotDict with one round and a deprecated name."""
        return DotDict(
            {"c": _round("c")},
            deprecated_names={"old_c": "c"},
        )

    def test_combines_codename_round_pairs(
        self, left: DotDict[Round], right: DotDict[Round]
    ) -> None:
        """The combined DotDict contains all rounds from both operands."""
        combined = left + right
        assert combined["a"] is left["a"]
        assert combined["c"] is right["c"]
        assert len(combined) == 3

    def test_returns_new_dotdict(
        self, left: DotDict[Round], right: DotDict[Round]
    ) -> None:
        """Addition returns a new DotDict and leaves operands unchanged."""
        combined = left + right
        assert isinstance(combined, DotDict)
        assert combined is not left
        assert combined is not right
        assert list(left.keys()) == ["a", "b"]
        assert list(right.keys()) == ["c"]

    def test_combines_deprecated_names(
        self, left: DotDict[Round], right: DotDict[Round]
    ) -> None:
        """Deprecated names from both operands resolve in the combined DotDict."""
        combined = left + right
        with pytest.warns(DeprecationWarning):
            assert combined["old_a"] is combined["a"]
            assert combined["old_c"] is combined["c"]

    def test_deprecated_name_resolves_across_operands(self) -> None:
        """A deprecated name may point to a codename from the other operand."""
        left: DotDict[Round] = DotDict(
            {"a": _round("a")}, deprecated_names={"old_c": "c"}
        )
        right: DotDict[Round] = DotDict({"c": _round("c")})
        combined = left + right
        with pytest.warns(DeprecationWarning):
            assert combined["old_c"] is combined["c"]

    def test_duplicate_codename_raises(self) -> None:
        """Two DotDicts sharing a codename cannot be combined."""
        left: DotDict[Round] = DotDict({"a": _round("a")})
        right: DotDict[Round] = DotDict({"a": _round("a"), "b": _round("b")})
        with pytest.raises(ValueError, match=r"Duplicate codename.*\['a'\]"):
            _ = left + right

    def test_duplicate_deprecated_name_raises(self) -> None:
        """Two DotDicts declaring the same deprecated name cannot be combined."""
        left: DotDict[Round] = DotDict(
            {"a": _round("a")}, deprecated_names={"old": "a"}
        )
        right: DotDict[Round] = DotDict(
            {"b": _round("b")}, deprecated_names={"old": "b"}
        )
        with pytest.raises(ValueError, match=r"Duplicate deprecated name.*\['old'\]"):
            _ = left + right

    @pytest.mark.parametrize("reverse", [False, True])
    def test_deprecated_name_clash_with_codename_raises(self, reverse: bool) -> None:
        """A deprecated name clashing with a combined codename is rejected."""
        with_deprecated: DotDict[Round] = DotDict(
            {"a": _round("a")}, deprecated_names={"b": "a"}
        )
        with_canonical: DotDict[Round] = DotDict({"b": _round("b")})
        operands = (
            (with_canonical, with_deprecated)
            if reverse
            else (with_deprecated, with_canonical)
        )
        with pytest.raises(ValueError, match="clash"):
            _ = operands[0] + operands[1]

    def test_add_non_dotdict_raises_typeerror(self) -> None:
        """Adding a non-DotDict operand is not supported."""
        dd: DotDict[Round] = DotDict({"a": _round("a")})
        with pytest.raises(TypeError):
            _ = dd + {"b": _round("b")}  # type: ignore[operator]


class TestDefaultRoundsLoad:
    """Smoke tests for bundled round collections."""

    def test_default_rounds_load_without_error(self) -> None:
        """Bundled rounds (which have no deprecations) load without error."""
        assert len(load_rounds.AGB_indoor) > 0
        assert isinstance(load_rounds.AGB_indoor, DotDict)
