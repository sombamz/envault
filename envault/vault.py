"""Vault storage: read/write encrypted profile files."""

import json
import os
from pathlib import Path

from envault.crypto import encrypt, decrypt

DEFAULT_VAULT_DIR = Path.home() / ".envault" / "vaults"


def _vault_path(profile: str, vault_dir: Path) -> Path:
    return vault_dir / f"{profile}.vault"


def save_profile(profile: str, variables: dict[str, str], password: str, vault_dir: Path = DEFAULT_VAULT_DIR) -> Path:
    """Encrypt and persist *variables* for *profile*."""
    vault_dir.mkdir(parents=True, exist_ok=True)
    plaintext = json.dumps(variables)
    ciphertext = encrypt(plaintext, password)
    path = _vault_path(profile, vault_dir)
    path.write_bytes(ciphertext)
    return path


def load_profile(profile: str, password: str, vault_dir: Path = DEFAULT_VAULT_DIR) -> dict[str, str]:
    """Decrypt and return variables for *profile*.

    Raises ``FileNotFoundError`` if the profile does not exist.
    Raises ``ValueError`` on decryption failure.
    """
    path = _vault_path(profile, vault_dir)
    if not path.exists():
        raise FileNotFoundError(f"Profile '{profile}' not found in vault.")
    ciphertext = path.read_bytes()
    plaintext = decrypt(ciphertext, password)
    return json.loads(plaintext)


def list_profiles(vault_dir: Path = DEFAULT_VAULT_DIR) -> list[str]:
    """Return sorted list of stored profile names."""
    if not vault_dir.exists():
        return []
    return sorted(p.stem for p in vault_dir.glob("*.vault"))


def delete_profile(profile: str, vault_dir: Path = DEFAULT_VAULT_DIR) -> None:
    """Remove a profile vault file."""
    path = _vault_path(profile, vault_dir)
    if not path.exists():
        raise FileNotFoundError(f"Profile '{profile}' not found.")
    path.unlink()
