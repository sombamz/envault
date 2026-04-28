"""Tests for envault.export serialization helpers."""

import json

import pytest

from envault.export import from_dotenv, to_dotenv, to_json, to_shell

SAMPLE = {"API_KEY": "secret123", "DEBUG": "true", "PORT": "8080"}


def test_to_dotenv_format():
    result = to_dotenv(SAMPLE)
    assert 'API_KEY="secret123"' in result
    assert 'DEBUG="true"' in result
    assert result.endswith("\n")


def test_to_dotenv_escapes_quotes():
    result = to_dotenv({"MSG": 'say "hello"'})
    assert 'MSG="say \\"hello\\""' in result


def test_to_dotenv_empty():
    assert to_dotenv({}) == ""


def test_to_json_valid():
    result = to_json(SAMPLE)
    parsed = json.loads(result)
    assert parsed == SAMPLE


def test_to_json_sorted_keys():
    result = to_json(SAMPLE)
    keys = list(json.loads(result).keys())
    assert keys == sorted(keys)


def test_to_shell_has_shebang():
    result = to_shell(SAMPLE)
    assert result.startswith("#!/bin/sh")


def test_to_shell_export_statements():
    result = to_shell(SAMPLE)
    assert "export API_KEY='secret123'" in result
    assert "export PORT='8080'" in result


def test_to_shell_escapes_single_quotes():
    result = to_shell({"VAR": "it's alive"})
    assert "export VAR='it'\\''s alive'" in result


def test_from_dotenv_basic():
    content = 'FOO="bar"\nBAZ="qux"\n'
    result = from_dotenv(content)
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_from_dotenv_ignores_comments():
    content = '# comment\nKEY="value"'
    result = from_dotenv(content)
    assert "KEY" in result
    assert len(result) == 1


def test_from_dotenv_unquoted_value():
    result = from_dotenv("PORT=9000")
    assert result["PORT"] == "9000"


def test_dotenv_round_trip():
    serialized = to_dotenv(SAMPLE)
    recovered = from_dotenv(serialized)
    assert recovered == SAMPLE
