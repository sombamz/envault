"""Tests for envault.rotation."""

from __future__ import annotations

import pytest

from envault.rotation import rotate_key, _key_hint
from envault.vault import save_profile, load_profile


# ---------------------------------------------------------------------------
# _key_hint
# ---------------------------------------------------------------------------

def test_key_hint_masks_password():
    hint = _key_hint("supersecret")
    assert hint.startswith("su")
    assert "*" in hint
    assert "persecret" not in hint


def test_key_hint_short_password():
    assert _key_hint("a") == "*"
    assert _key_hint("") == ""


# ---------------------------------------------------------------------------
# rotate_key
# ---------------------------------------------------------------------------

def test_rotate_key_success(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))

    save_profile("myapp", "oldpass", {"KEY": "value"})
    result = rotate_key("myapp", "oldpass", "newpass")

    assert result.success is True
    assert result.profile == "myapp"
    assert result.error is None

    # Verify new password works
    data = load_profile("myapp", "newpass")
    assert data["KEY"] == "value"


def test_rotate_key_old_password_no_longer_works(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))

    save_profile("myapp", "oldpass", {"SECRET": "xyz"})
    rotate_key("myapp", "oldpass", "newpass")

    with pytest.raises(Exception):
        load_profile("myapp", "oldpass")


def test_rotate_key_wrong_old_password_returns_failure(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))

    save_profile("myapp", "correct", {"A": "1"})
    result = rotate_key("myapp", "wrongpass", "newpass")

    assert result.success is False
    assert result.error is not None


def test_rotate_key_missing_profile_returns_failure(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))

    result = rotate_key("ghost", "any", "newpass")

    assert result.success is False
    assert result.error is not None


def test_rotate_key_hint_stored(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))

    save_profile("myapp", "oldpass", {})
    result = rotate_key("myapp", "oldpass", "newpass")

    assert result.previous_key_hint == "ol" + "*" * (len("oldpass") - 2)
