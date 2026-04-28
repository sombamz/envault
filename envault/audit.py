"""Audit log for tracking vault access and modifications."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def _audit_log_path() -> Path:
    """Return the path to the audit log file."""
    base = Path(os.environ.get("ENVAULT_DIR", Path.home() / ".envault"))
    base.mkdir(parents=True, exist_ok=True)
    return base / "audit.log"


def record_event(
    action: str,
    profile: str,
    success: bool = True,
    details: Optional[str] = None,
) -> None:
    """Append a structured audit event to the log file.

    Args:
        action: The action performed (e.g. 'set', 'inject', 'delete', 'export').
        profile: The profile name involved in the action.
        success: Whether the action succeeded.
        details: Optional extra context or error message.
    """
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "profile": profile,
        "success": success,
    }
    if details:
        event["details"] = details

    log_path = _audit_log_path()
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event) + "\n")


def read_events(profile: Optional[str] = None, limit: int = 50) -> list[dict]:
    """Read audit log events, optionally filtered by profile.

    Args:
        profile: If provided, only return events for this profile.
        limit: Maximum number of recent events to return.

    Returns:
        A list of event dicts, most recent last.
    """
    log_path = _audit_log_path()
    if not log_path.exists():
        return []

    events: list[dict] = []
    with log_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if profile is None or event.get("profile") == profile:
                events.append(event)

    return events[-limit:]


def clear_log() -> None:
    """Erase all audit log entries (used in tests or by admin command)."""
    log_path = _audit_log_path()
    if log_path.exists():
        log_path.unlink()
