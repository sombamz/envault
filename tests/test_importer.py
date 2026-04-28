"""Tests for envault.importer file-based import helpers."""

import json
from pathlib import Path

import pytest

from envault.importer import ImportError as VaultImportError
from envault.importer import import_from_file


@pytest.fixture()
def tmp_env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text('DB_URL="postgres://localhost/db"\nSECRET="abc123"\n', encoding="utf-8")
    return p


@pytest.fixture()
def tmp_json_file(tmp_path: Path) -> Path:
    p = tmp_path / "vars.json"
    p.write_text(json.dumps({"HOST": "localhost", "PORT": "5432"}), encoding="utf-8")
    return p


@pytest.fixture()
def tmp_shell_file(tmp_path: Path) -> Path:
    p = tmp_path / "env.sh"
    p.write_text("#!/bin/sh\nexport APP_ENV='production'\nexport LOG_LEVEL='info'\n", encoding="utf-8")
    return p


def test_import_dotenv(tmp_env_file: Path):
    result = import_from_file(str(tmp_env_file))
    assert result["DB_URL"] == "postgres://localhost/db"
    assert result["SECRET"] == "abc123"


def test_import_json(tmp_json_file: Path):
    result = import_from_file(str(tmp_json_file))
    assert result["HOST"] == "localhost"
    assert result["PORT"] == "5432"


def test_import_shell(tmp_shell_file: Path):
    result = import_from_file(str(tmp_shell_file))
    assert result["APP_ENV"] == "production"
    assert result["LOG_LEVEL"] == "info"


def test_import_missing_file():
    with pytest.raises(VaultImportError, match="File not found"):
        import_from_file("/nonexistent/path/.env")


def test_import_invalid_json(tmp_path: Path):
    bad = tmp_path / "bad.json"
    bad.write_text("not valid json", encoding="utf-8")
    with pytest.raises(VaultImportError, match="Invalid JSON"):
        import_from_file(str(bad))


def test_import_json_non_object(tmp_path: Path):
    bad = tmp_path / "list.json"
    bad.write_text(json.dumps(["a", "b"]), encoding="utf-8")
    with pytest.raises(VaultImportError, match="top-level object"):
        import_from_file(str(bad))


def test_force_format_override(tmp_path: Path):
    """Force dotenv parsing on a file with no recognised extension."""
    f = tmp_path / "myconfig"
    f.write_text('FORCED="yes"\n', encoding="utf-8")
    result = import_from_file(str(f), fmt="dotenv")
    assert result["FORCED"] == "yes"
