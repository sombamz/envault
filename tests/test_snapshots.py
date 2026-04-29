"""Unit tests for envault.snapshots."""
from __future__ import annotations

import os
import time

import pytest

from envault.snapshots import (
    delete_snapshot,
    list_snapshots,
    load_snapshot,
    save_snapshot,
)


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_HOME", str(tmp_path))
    yield tmp_path


VARS = {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_save_snapshot_returns_snapshot_object():
    snap = save_snapshot("prod", VARS)
    assert snap.profile == "prod"
    assert snap.variables == VARS
    assert snap.label is None
    assert snap.timestamp > 0


def test_save_snapshot_with_label():
    snap = save_snapshot("prod", VARS, label="before-migration")
    assert snap.label == "before-migration"
    assert "before-migration" in snap.snapshot_id


def test_snapshot_id_contains_profile_and_timestamp():
    snap = save_snapshot("staging", VARS)
    assert "staging" in snap.snapshot_id
    assert str(int(snap.timestamp)) in snap.snapshot_id


def test_load_snapshot_round_trip():
    snap = save_snapshot("dev", VARS, label="v1")
    loaded = load_snapshot(snap.snapshot_id)
    assert loaded.profile == snap.profile
    assert loaded.variables == snap.variables
    assert loaded.label == snap.label


def test_load_missing_snapshot_raises():
    with pytest.raises(FileNotFoundError):
        load_snapshot("nonexistent_000")


def test_list_snapshots_returns_all():
    save_snapshot("alpha", VARS)
    save_snapshot("beta", VARS)
    snaps = list_snapshots()
    profiles = {s.profile for s in snaps}
    assert "alpha" in profiles
    assert "beta" in profiles


def test_list_snapshots_filtered_by_profile():
    save_snapshot("alpha", VARS)
    save_snapshot("beta", VARS)
    snaps = list_snapshots(profile="alpha")
    assert all(s.profile == "alpha" for s in snaps)


def test_list_snapshots_empty_when_none():
    assert list_snapshots() == []


def test_delete_snapshot_removes_file():
    snap = save_snapshot("prod", VARS)
    delete_snapshot(snap.snapshot_id)
    with pytest.raises(FileNotFoundError):
        load_snapshot(snap.snapshot_id)


def test_delete_missing_snapshot_raises():
    with pytest.raises(FileNotFoundError):
        delete_snapshot("ghost_000")
