"""Snapshot support: capture and restore profile states."""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


def _snapshot_dir() -> Path:
    base = Path(os.environ.get("ENVAULT_HOME", Path.home() / ".envault"))
    snap_dir = base / "snapshots"
    snap_dir.mkdir(parents=True, exist_ok=True)
    return snap_dir


@dataclass
class Snapshot:
    profile: str
    timestamp: float
    label: Optional[str]
    variables: Dict[str, str]

    @property
    def snapshot_id(self) -> str:
        ts = int(self.timestamp)
        suffix = f"_{self.label}" if self.label else ""
        return f"{self.profile}_{ts}{suffix}"


def save_snapshot(
    profile: str, variables: Dict[str, str], label: Optional[str] = None
) -> Snapshot:
    """Persist a snapshot of *variables* for *profile*."""
    snap = Snapshot(
        profile=profile,
        timestamp=time.time(),
        label=label,
        variables=variables,
    )
    path = _snapshot_dir() / f"{snap.snapshot_id}.json"
    path.write_text(
        json.dumps(
            {
                "profile": snap.profile,
                "timestamp": snap.timestamp,
                "label": snap.label,
                "variables": snap.variables,
            },
            indent=2,
        )
    )
    return snap


def load_snapshot(snapshot_id: str) -> Snapshot:
    """Load a snapshot by its ID. Raises FileNotFoundError if absent."""
    path = _snapshot_dir() / f"{snapshot_id}.json"
    data = json.loads(path.read_text())
    return Snapshot(**data)


def list_snapshots(profile: Optional[str] = None) -> List[Snapshot]:
    """Return all snapshots, optionally filtered by *profile*."""
    snaps: List[Snapshot] = []
    for p in sorted(_snapshot_dir().glob("*.json")):
        data = json.loads(p.read_text())
        snap = Snapshot(**data)
        if profile is None or snap.profile == profile:
            snaps.append(snap)
    return snaps


def delete_snapshot(snapshot_id: str) -> None:
    """Remove a snapshot file. Raises FileNotFoundError if absent."""
    path = _snapshot_dir() / f"{snapshot_id}.json"
    path.unlink()
