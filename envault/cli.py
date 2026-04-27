"""Command-line interface for envault."""

import os
import sys
import click
from getpass import getpass

from envault.vault import save_profile, load_profile, list_profiles, delete_profile


@click.group()
def cli() -> None:
    """envault — securely manage and inject environment variables."""


@cli.command("set")
@click.argument("profile")
@click.argument("key_value_pairs", nargs=-1, required=True)
def set_vars(profile: str, key_value_pairs: tuple[str, ...]) -> None:
    """Set KEY=VALUE pairs in PROFILE."""
    variables = {}
    for pair in key_value_pairs:
        if "=" not in pair:
            click.echo(f"Invalid format: '{pair}'. Expected KEY=VALUE.", err=True)
            sys.exit(1)
        k, _, v = pair.partition("=")
        variables[k.strip()] = v.strip()

    password = getpass(f"Password for profile '{profile}': ")
    # Merge with existing if possible
    try:
        existing = load_profile(profile, password)
        existing.update(variables)
        variables = existing
    except FileNotFoundError:
        pass

    path = save_profile(profile, variables, password)
    click.echo(f"Saved {len(variables)} variable(s) to profile '{profile}' ({path}).")


@cli.command("inject")
@click.argument("profile")
@click.argument("command", nargs=-1, required=True)
def inject(profile: str, command: tuple[str, ...]) -> None:
    """Run COMMAND with PROFILE variables injected into the environment."""
    password = getpass(f"Password for profile '{profile}': ")
    variables = load_profile(profile, password)
    env = {**os.environ, **variables}
    os.execvpe(command[0], list(command), env)


@cli.command("list")
def list_cmd() -> None:
    """List all stored profiles."""
    profiles = list_profiles()
    if not profiles:
        click.echo("No profiles found.")
    for name in profiles:
        click.echo(f"  {name}")


@cli.command("delete")
@click.argument("profile")
@click.confirmation_option(prompt="Are you sure you want to delete this profile?")
def delete_cmd(profile: str) -> None:
    """Delete a stored profile."""
    delete_profile(profile)
    click.echo(f"Profile '{profile}' deleted.")


if __name__ == "__main__":
    cli()
