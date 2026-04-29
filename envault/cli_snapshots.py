"""CLI commands for profile snapshots."""
from __future__ import annotations

import click

from envault.audit import record_event
from envault.snapshots import (
    delete_snapshot,
    list_snapshots,
    load_snapshot,
    save_snapshot,
)
from envault.vault import load_profile, save_profile


@click.group("snapshot")
def snapshot_cmd() -> None:
    """Manage profile snapshots."""


@snapshot_cmd.command("create")
@click.argument("profile")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--label", default=None, help="Optional human-readable label.")
def create_snapshot(profile: str, password: str, label: str | None) -> None:
    """Snapshot the current state of PROFILE."""
    try:
        variables = load_profile(profile, password)
    except Exception as exc:  # noqa: BLE001
        record_event("snapshot_create", profile, success=False, detail=str(exc))
        raise click.ClickException(str(exc)) from exc

    snap = save_snapshot(profile, variables, label=label)
    record_event("snapshot_create", profile, success=True, detail=snap.snapshot_id)
    click.echo(f"Snapshot created: {snap.snapshot_id}")


@snapshot_cmd.command("list")
@click.argument("profile", required=False, default=None)
def list_snapshots_cmd(profile: str | None) -> None:
    """List snapshots, optionally filtered by PROFILE."""
    snaps = list_snapshots(profile)
    if not snaps:
        click.echo("No snapshots found.")
        return
    for snap in snaps:
        label_part = f"  [{snap.label}]" if snap.label else ""
        click.echo(f"{snap.snapshot_id}{label_part}  ({snap.profile})")


@snapshot_cmd.command("restore")
@click.argument("snapshot_id")
@click.option("--password", prompt=True, hide_input=True)
def restore_snapshot(snapshot_id: str, password: str) -> None:
    """Restore a profile from SNAPSHOT_ID."""
    try:
        snap = load_snapshot(snapshot_id)
        save_profile(snap.profile, snap.variables, password)
    except FileNotFoundError as exc:
        record_event("snapshot_restore", snapshot_id, success=False, detail=str(exc))
        raise click.ClickException(f"Snapshot not found: {snapshot_id}") from exc
    except Exception as exc:  # noqa: BLE001
        record_event("snapshot_restore", snapshot_id, success=False, detail=str(exc))
        raise click.ClickException(str(exc)) from exc

    record_event("snapshot_restore", snap.profile, success=True, detail=snapshot_id)
    click.echo(f"Profile '{snap.profile}' restored from snapshot {snapshot_id}.")


@snapshot_cmd.command("delete")
@click.argument("snapshot_id")
@click.confirmation_option(prompt="Are you sure you want to delete this snapshot?")
def delete_snapshot_cmd(snapshot_id: str) -> None:
    """Permanently delete SNAPSHOT_ID."""
    try:
        delete_snapshot(snapshot_id)
    except FileNotFoundError as exc:
        raise click.ClickException(f"Snapshot not found: {snapshot_id}") from exc
    record_event("snapshot_delete", snapshot_id, success=True)
    click.echo(f"Snapshot {snapshot_id} deleted.")
