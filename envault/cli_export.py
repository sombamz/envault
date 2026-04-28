"""CLI commands for exporting and importing vault profiles."""

import sys
from pathlib import Path

import click

from envault.export import FORMATS
from envault.importer import ImportError as VaultImportError
from envault.importer import import_from_file
from envault.vault import load_profile, save_profile


@click.command("export")
@click.argument("profile")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option(
    "--format", "fmt",
    type=click.Choice(list(FORMATS.keys())),
    default="dotenv",
    show_default=True,
    help="Output format.",
)
@click.option("--output", "-o", default=None, help="Output file path (stdout if omitted).")
def export_cmd(profile: str, password: str, fmt: str, output: str | None) -> None:
    """Export a profile's variables to a file or stdout."""
    try:
        variables = load_profile(profile, password)
    except FileNotFoundError:
        click.echo(f"Profile '{profile}' not found.", err=True)
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Error loading profile: {exc}", err=True)
        sys.exit(1)

    serializer = FORMATS[fmt]
    content = serializer(variables)

    if output:
        Path(output).write_text(content, encoding="utf-8")
        click.echo(f"Exported {len(variables)} variable(s) to '{output}'.")
    else:
        click.echo(content, nl=False)


@click.command("import")
@click.argument("profile")
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option(
    "--format", "fmt",
    type=click.Choice(["dotenv", "json", "shell"]),
    default=None,
    help="Force input format (auto-detected by default).",
)
@click.option("--merge", is_flag=True, default=False, help="Merge with existing profile.")
def import_cmd(profile: str, file_path: str, password: str, fmt: str | None, merge: bool) -> None:
    """Import variables from a file into a vault profile."""
    try:
        new_vars = import_from_file(file_path, fmt)
    except VaultImportError as exc:
        click.echo(f"Import error: {exc}", err=True)
        sys.exit(1)

    variables = {}
    if merge:
        try:
            variables = load_profile(profile, password)
        except FileNotFoundError:
            pass  # profile doesn't exist yet — that's fine
        except Exception as exc:  # noqa: BLE001
            click.echo(f"Error loading existing profile: {exc}", err=True)
            sys.exit(1)

    variables.update(new_vars)
    save_profile(profile, variables, password)
    click.echo(f"Imported {len(new_vars)} variable(s) into profile '{profile}'.")
