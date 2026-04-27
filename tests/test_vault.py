"""Tests for envault.vault."""

import pytest
from pathlib import Path
from envault.vault import save_profile, load_profile, list_profiles, delete_profile


PROFILE = "test-project"
PASSWORD = "vault-password-123"
VARS = {"API_KEY": "abc123", "DEBUG": "true"}


@pytest.fixture()
def vault_dir(tmp_path: Path) -> Path:
    return tmp_path / "vaults"


def test_save_and_load(vault_dir):
    save_profile(PROFILE, VARS, PASSWORD, vault_dir)
    loaded = load_profile(PROFILE, PASSWORD, vault_dir)
    assert loaded == VARS


def test_vault_file_created(vault_dir):
    path = save_profile(PROFILE, VARS, PASSWORD, vault_dir)
    assert path.exists()


def test_load_missing_profile_raises(vault_dir):
    with pytest.raises(FileNotFoundError, match="not found"):
        load_profile("nonexistent", PASSWORD, vault_dir)


def test_wrong_password_raises(vault_dir):
    save_profile(PROFILE, VARS, PASSWORD, vault_dir)
    with pytest.raises(ValueError):
        load_profile(PROFILE, "bad-password", vault_dir)


def test_list_profiles(vault_dir):
    save_profile("alpha", VARS, PASSWORD, vault_dir)
    save_profile("beta", VARS, PASSWORD, vault_dir)
    assert list_profiles(vault_dir) == ["alpha", "beta"]


def test_list_profiles_empty(vault_dir):
    assert list_profiles(vault_dir) == []


def test_delete_profile(vault_dir):
    save_profile(PROFILE, VARS, PASSWORD, vault_dir)
    delete_profile(PROFILE, vault_dir)
    assert list_profiles(vault_dir) == []


def test_delete_missing_profile_raises(vault_dir):
    with pytest.raises(FileNotFoundError):
        delete_profile("ghost", vault_dir)
