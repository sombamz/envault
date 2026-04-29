"""CLI integration tests for snapshot commands."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envault.cli_snapshots import snapshot_cmd
from envault.snapshots import save_snapshot
from envault.vault import save_profile

VARS = {"SECRET": "abc123", "PORT": "8080"}
PASSWORD = "test-pass"


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_HOME", str(tmp_path))
    yield


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def saved_profile():
    save_profile("prod", VARS, PASSWORD)


def test_create_snapshot_success(runner, saved_profile):
    result = runner.invoke(
        snapshot_cmd, ["create", "prod", "--password", PASSWORD]
    )
    assert result.exit_code == 0
    assert "Snapshot created" in result.output


def test_create_snapshot_with_label(runner, saved_profile):
    result = runner.invoke(
        snapshot_cmd,
        ["create", "prod", "--password", PASSWORD, "--label", "pre-deploy"],
    )
    assert result.exit_code == 0
    assert "pre-deploy" in result.output


def test_create_snapshot_wrong_password(runner, saved_profile):
    result = runner.invoke(
        snapshot_cmd, ["create", "prod", "--password", "wrong"]
    )
    assert result.exit_code != 0


def test_list_snapshots_shows_entries(runner, saved_profile):
    runner.invoke(snapshot_cmd, ["create", "prod", "--password", PASSWORD])
    result = runner.invoke(snapshot_cmd, ["list"])
    assert result.exit_code == 0
    assert "prod" in result.output


def test_list_snapshots_empty(runner):
    result = runner.invoke(snapshot_cmd, ["list"])
    assert result.exit_code == 0
    assert "No snapshots found" in result.output


def test_restore_snapshot_success(runner, saved_profile):
    snap = save_snapshot("prod", {"RESTORED": "yes"})
    result = runner.invoke(
        snapshot_cmd,
        ["restore", snap.snapshot_id, "--password", PASSWORD],
    )
    assert result.exit_code == 0
    assert "restored" in result.output


def test_restore_missing_snapshot(runner):
    result = runner.invoke(
        snapshot_cmd, ["restore", "ghost_000", "--password", PASSWORD]
    )
    assert result.exit_code != 0
    assert "not found" in result.output.lower()


def test_delete_snapshot(runner, saved_profile):
    snap = save_snapshot("prod", VARS)
    result = runner.invoke(
        snapshot_cmd, ["delete", snap.snapshot_id, "--yes"]
    )
    assert result.exit_code == 0
    assert "deleted" in result.output
