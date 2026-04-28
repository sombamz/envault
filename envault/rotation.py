"""Key rotation support for envault profiles."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from envault.vault import load_profile, save_profile
from envault.audit import record_event


@dataclass
class RotationResult:
    profile: str
    rotated_at: str
    previous_key_hint: str
    success: bool
    error: Optional[str] = None


def _key_hint(password: str) -> str:
    """Return a short non-reversible hint for a password (first 2 + length)."""
    if len(password) < 2:
        return "*" * len(password)
    return password[:2] + "*" * (len(password) - 2)


def rotate_key(
    profile: str,
    old_password: str,
    new_password: str,
) -> RotationResult:
    """Re-encrypt a profile's secrets under a new password.

    Loads the profile with *old_password*, then immediately saves it back
    encrypted with *new_password*.  An audit event is recorded regardless
    of outcome.

    Raises:
        ValueError: if the profile cannot be decrypted with *old_password*.
    """
    hint = _key_hint(old_password)
    rotated_at = datetime.now(timezone.utc).isoformat()

    try:
        data = load_profile(profile, old_password)
        save_profile(profile, new_password, data)
        record_event("rotate_key", profile, success=True)
        return RotationResult(
            profile=profile,
            rotated_at=rotated_at,
            previous_key_hint=hint,
            success=True,
        )
    except Exception as exc:  # noqa: BLE001
        record_event("rotate_key", profile, success=False, detail=str(exc))
        return RotationResult(
            profile=profile,
            rotated_at=rotated_at,
            previous_key_hint=hint,
            success=False,
            error=str(exc),
        )
