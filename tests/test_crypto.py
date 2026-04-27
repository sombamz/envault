"""Tests for envault.crypto."""

import pytest
from envault.crypto import encrypt, decrypt, SALT_SIZE


PASSWORD = "super-secret-passphrase"
PLAINTEXT = "DATABASE_URL=postgres://localhost/mydb"


def test_encrypt_returns_bytes():
    result = encrypt(PLAINTEXT, PASSWORD)
    assert isinstance(result, bytes)


def test_encrypt_includes_salt():
    result = encrypt(PLAINTEXT, PASSWORD)
    assert len(result) > SALT_SIZE


def test_round_trip():
    ciphertext = encrypt(PLAINTEXT, PASSWORD)
    recovered = decrypt(ciphertext, PASSWORD)
    assert recovered == PLAINTEXT


def test_different_encryptions_differ():
    """Each call should produce a unique ciphertext (random salt)."""
    a = encrypt(PLAINTEXT, PASSWORD)
    b = encrypt(PLAINTEXT, PASSWORD)
    assert a != b


def test_wrong_password_raises():
    ciphertext = encrypt(PLAINTEXT, PASSWORD)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(ciphertext, "wrong-password")


def test_corrupted_data_raises():
    ciphertext = bytearray(encrypt(PLAINTEXT, PASSWORD))
    ciphertext[SALT_SIZE + 5] ^= 0xFF  # flip a bit in the token
    with pytest.raises(ValueError):
        decrypt(bytes(ciphertext), PASSWORD)
