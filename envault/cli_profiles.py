"""CLI commands for profile introspection and management."""

from __future__ import annotations

import click

from envault.profiles import Profile, merge_profiles, validate_profile_name
from envault.vault import load_profile, save_profile, list_profiles


@click.group("profile")
def profile_cmd() -> None:
    """Inspect and manage vault profiles."""


@profile_cmd.command("info")
@click.argument("profile")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
def info_cmd(profile: str, password: str) -> None:
    """Display metadata and variable keys for a profile."""
    try:
        variables = load_profile(profile, password)
    except FileNotFoundError:
        raise click.ClickException(f"Profile '{profile}' does not exist.")
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc))

    p = Profile(name=profile, variables=variables)
    click.echo(f"Profile : {p.name}")
    click.echo(f"Keys    : {len(p.variables)}")
    if p.variables:
        for key in p.keys():
            click.echo(f"  {key}")
    else:
        click.echo("  (empty)")


@profile_cmd.command("rename")
@click.argument("old_name")
@click.argument("new_name")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
def rename_cmd(old_name: str, new_name: str, password: str) -> None:
    """Rename a profile (re-encrypts under the same password)."""
    try:
        validate_profile_name(new_name)
    except ValueError as exc:
        raise click.ClickException(str(exc))

    if new_name in list_profiles():
        raise click.ClickException(f"Profile '{new_name}' already exists.")

    try:
        variables = load_profile(old_name, password)
    except FileNotFoundError:
        raise click.ClickException(f"Profile '{old_name}' does not exist.")
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc))

    save_profile(new_name, variables, password)
    from envault.vault import delete_profile
    delete_profile(old_name)
    click.echo(f"Profile '{old_name}' renamed to '{new_name}'.")


@profile_cmd.command("merge")
@click.argument("base")
@click.argument("override")
@click.argument("target")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
def merge_cmd(base: str, override: str, target: str, password: str) -> None:
    """Merge two profiles into a new target profile."""
    try:
        base_vars = load_profile(base, password)
        override_vars = load_profile(override, password)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc))

    base_p = Profile(name=base, variables=base_vars)
    override_p = Profile(name=override, variables=override_vars)
    merged = merge_profiles(base_p, override_p)

    save_profile(target, merged.variables, password)
    click.echo(
        f"Merged '{base}' + '{override}' -> '{target}' "
        f"({len(merged.variables)} variables)."
    )
