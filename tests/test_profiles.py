"""Tests for envault.profiles module."""

from __future__ import annotations

import pytest

from envault.profiles import (
    Profile,
    merge_profiles,
    validate_profile_name,
)


# ---------------------------------------------------------------------------
# validate_profile_name
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", ["dev", "prod-eu", "my.profile", "app_v2", "A" * 64])
def test_valid_profile_names(name: str) -> None:
    validate_profile_name(name)  # should not raise


@pytest.mark.parametrize("name", ["", "has space", "slash/name", "A" * 65, "!bad"])
def test_invalid_profile_names_raise(name: str) -> None:
    with pytest.raises(ValueError, match="Invalid profile name"):
        validate_profile_name(name)


# ---------------------------------------------------------------------------
# Profile dataclass
# ---------------------------------------------------------------------------


def test_profile_set_and_get() -> None:
    p = Profile(name="dev")
    p.set("KEY", "value")
    assert p.variables["KEY"] == "value"


def test_profile_set_empty_key_raises() -> None:
    p = Profile(name="dev")
    with pytest.raises(ValueError):
        p.set("", "value")


def test_profile_unset() -> None:
    p = Profile(name="dev", variables={"A": "1", "B": "2"})
    p.unset("A")
    assert "A" not in p.variables


def test_profile_unset_missing_raises() -> None:
    p = Profile(name="dev")
    with pytest.raises(KeyError):
        p.unset("MISSING")


def test_profile_keys_sorted() -> None:
    p = Profile(name="dev", variables={"Z": "1", "A": "2", "M": "3"})
    assert p.keys() == ["A", "M", "Z"]


def test_profile_round_trip_dict() -> None:
    p = Profile(name="staging", variables={"FOO": "bar"}, description="staging env")
    restored = Profile.from_dict(p.to_dict())
    assert restored.name == p.name
    assert restored.variables == p.variables
    assert restored.description == p.description


def test_profile_invalid_name_raises_on_init() -> None:
    with pytest.raises(ValueError):
        Profile(name="bad name!")


# ---------------------------------------------------------------------------
# merge_profiles
# ---------------------------------------------------------------------------


def test_merge_profiles_override_wins() -> None:
    base = Profile(name="base", variables={"A": "1", "B": "2"})
    override = Profile(name="override", variables={"B": "99", "C": "3"})
    merged = merge_profiles(base, override)
    assert merged.variables == {"A": "1", "B": "99", "C": "3"}


def test_merge_profiles_preserves_base_name() -> None:
    base = Profile(name="base", variables={"X": "1"})
    override = Profile(name="override", variables={"Y": "2"})
    merged = merge_profiles(base, override)
    assert merged.name == "base"


def test_merge_profiles_empty_override() -> None:
    base = Profile(name="base", variables={"A": "1"})
    override = Profile(name="override")
    merged = merge_profiles(base, override)
    assert merged.variables == {"A": "1"}
