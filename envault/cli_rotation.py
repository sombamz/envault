"""CLI commands for key rotation."""

from __future__ import annotations

import click

from envault.rotation import rotate_key


@click.group("rotation")
def rotation_cmd() -> None:
    """Key rotation commands."""


@rotation_cmd.command("rotate")
@click.argument("profile")
@click.option(
    "--old-password",
    prompt=True,
    hide_input=True,
    help="Current encryption password.",
)
@click.option(
    "--new-password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="New encryption password.",
)
def rotate(
    profile: str,
    old_password: str,
    new_password: str,
) -> None:
    """Re-encrypt PROFILE secrets under a new password."""
    if old_password == new_password:
        raise click.UsageError("New password must differ from the old password.")

    result = rotate_key(profile, old_password, new_password)

    if result.success:
        click.echo(
            click.style(
                f"✓ Profile '{profile}' re-encrypted successfully at {result.rotated_at}.",
                fg="green",
            )
        )
    else:
        click.echo(
            click.style(
                f"✗ Rotation failed for '{profile}': {result.error}",
                fg="red",
            ),
            err=True,
        )
        raise SystemExit(1)
