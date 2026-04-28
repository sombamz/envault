"""Tests for envault.cli_rotation CLI commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_rotation import rotation_cmd
from envault.vault import save_profile, load_profile


@pytest.fixture()
def runner():
    return CliRunner(mix_stderr=False)


def test_rotate_success(tmp_path, monkeypatch, runner):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    save_profile("app", "old", {"X": "1"})

    result = runner.invoke(
        rotation_cmd,
        ["rotate", "app", "--old-password", "old", "--new-password", "new"],
    )

    assert result.exit_code == 0
    assert "re-encrypted successfully" in result.output


def test_rotate_wrong_old_password(tmp_path, monkeypatch, runner):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    save_profile("app", "correct", {"X": "1"})

    result = runner.invoke(
        rotation_cmd,
        ["rotate", "app", "--old-password", "wrong", "--new-password", "new"],
    )

    assert result.exit_code != 0


def test_rotate_same_password_rejected(tmp_path, monkeypatch, runner):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))

    result = runner.invoke(
        rotation_cmd,
        ["rotate", "app", "--old-password", "same", "--new-password", "same"],
    )

    assert result.exit_code != 0
    assert "differ" in result.output


def test_rotate_data_intact_after_rotation(tmp_path, monkeypatch, runner):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    save_profile("app", "old", {"DB": "postgres", "PORT": "5432"})

    runner.invoke(
        rotation_cmd,
        ["rotate", "app", "--old-password", "old", "--new-password", "new"],
    )

    data = load_profile("app", "new")
    assert data["DB"] == "postgres"
    assert data["PORT"] == "5432"
