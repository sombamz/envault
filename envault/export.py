"""Export profiles to various formats (dotenv, JSON, shell script)."""

import json
from typing import Dict


def to_dotenv(variables: Dict[str, str]) -> str:
    """Serialize variables to .env file format."""
    lines = []
    for key, value in sorted(variables.items()):
        escaped = value.replace('"', '\\"')
        lines.append(f'{key}="{escaped}"')
    return "\n".join(lines) + "\n" if lines else ""


def to_json(variables: Dict[str, str]) -> str:
    """Serialize variables to JSON format."""
    return json.dumps(variables, indent=2, sort_keys=True) + "\n"


def to_shell(variables: Dict[str, str]) -> str:
    """Serialize variables to shell export statements."""
    lines = ["#!/bin/sh"]
    for key, value in sorted(variables.items()):
        escaped = value.replace("'", "'\\''")
        lines.append(f"export {key}='{escaped}'")
    return "\n".join(lines) + "\n"


def from_dotenv(content: str) -> Dict[str, str]:
    """Parse variables from .env file format."""
    variables = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
            value = value[1:-1].replace('\\"', '"')
        variables[key] = value
    return variables


FORMATS = {
    "dotenv": to_dotenv,
    "json": to_json,
    "shell": to_shell,
}
