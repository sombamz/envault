"""Import variables from external files into a vault profile."""

import json
from pathlib import Path
from typing import Dict

from envault.export import from_dotenv


class ImportError(Exception):  # noqa: A001
    """Raised when an import operation fails."""


def _detect_format(path: Path) -> str:
    """Detect file format by extension."""
    suffix = path.suffix.lower()
    if suffix in (".env", ".envrc"):
        return "dotenv"
    if suffix == ".json":
        return "json"
    if suffix in (".sh", ".bash"):
        return "shell"
    return "dotenv"  # default fallback


def import_from_file(file_path: str, fmt: str | None = None) -> Dict[str, str]:
    """Read and parse environment variables from a file."""
    path = Path(file_path)
    if not path.exists():
        raise ImportError(f"File not found: {file_path}")

    resolved_fmt = fmt or _detect_format(path)
    content = path.read_text(encoding="utf-8")

    if resolved_fmt == "dotenv":
        return from_dotenv(content)
    if resolved_fmt == "json":
        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ImportError(f"Invalid JSON: {exc}") from exc
        if not isinstance(data, dict):
            raise ImportError("JSON file must contain a top-level object.")
        return {str(k): str(v) for k, v in data.items()}
    if resolved_fmt == "shell":
        variables: Dict[str, str] = {}
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("export "):
                line = line[len("export "):]
            if "=" not in line or line.startswith("#"):
                continue
            key, _, value = line.partition("=")
            value = value.strip("'\"")
            variables[key.strip()] = value
        return variables

    raise ImportError(f"Unsupported format: {resolved_fmt}")
