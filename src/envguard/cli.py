"""CLI entry point for EnvGuard."""

from __future__ import annotations

import sys
from pathlib import Path

import click
from rich.console import Console

from envguard import __version__
from envguard.auditor import audit_env
from envguard.checker import check_env
from envguard.generator import generate_example
from envguard.reporter import print_audit_report, print_check_report, print_diff_report

console = Console()

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(__version__, "-V", "--version")
def main() -> None:
    """EnvGuard — never ship broken environment configs again."""


# ---------------------------------------------------------------------------
# envguard check
# ---------------------------------------------------------------------------

@main.command()
@click.option(
    "--env",
    "env_path",
    default=".env",
    show_default=True,
    type=click.Path(exists=False),
    help="Path to the .env file to validate.",
)
@click.option(
    "--example",
    "example_path",
    default=".env.example",
    show_default=True,
    type=click.Path(exists=False),
    help="Path to the .env.example template.",
)
@click.option(
    "--format",
    "output_format",
    default="text",
    type=click.Choice(["text", "json"], case_sensitive=False),
    help="Output format.",
)
@click.option(
    "--fail-on-warning",
    is_flag=True,
    default=False,
    help="Exit with code 1 on warnings as well as errors.",
)
def check(
    env_path: str,
    example_path: str,
    output_format: str,
    fail_on_warning: bool,
) -> None:
    """Validate .env against .env.example.

    Finds missing required keys, undocumented extra keys, and empty values.
    Exits with code 1 if errors are found (or warnings when --fail-on-warning is set).
    """
    result = check_env(
        env_path=Path(env_path),
        example_path=Path(example_path),
    )
    print_check_report(result, output_format=output_format, console=console)

    has_errors = bool(result.missing or result.empty_required)
    has_warnings = bool(result.extra)

    if has_errors or (fail_on_warning and has_warnings):
        sys.exit(1)


# ---------------------------------------------------------------------------
# envguard audit
# ---------------------------------------------------------------------------

@main.command()
@click.option(
    "--env",
    "env_path",
    default=".env",
    show_default=True,
    type=click.Path(exists=False),
    help="Path to the .env file to audit.",
)
@click.option(
    "--format",
    "output_format",
    default="text",
    type=click.Choice(["text", "json"], case_sensitive=False),
)
def audit(env_path: str, output_format: str) -> None:
    """Scan for potential secret leaks in a .env file.

    Checks for suspicious patterns in key names and flags any keys whose
    values look like raw credentials (tokens, passwords, API keys).
    """
    findings = audit_env(Path(env_path))
    print_audit_report(findings, output_format=output_format, console=console)

    if findings:
        sys.exit(1)


# ---------------------------------------------------------------------------
# envguard generate
# ---------------------------------------------------------------------------

@main.command()
@click.option(
    "--env",
    "env_path",
    default=".env",
    show_default=True,
    type=click.Path(exists=False),
    help="Source .env file.",
)
@click.option(
    "--output",
    "output_path",
    default=".env.example",
    show_default=True,
    help="Destination path for the generated .env.example.",
)
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite output file if it already exists.",
)
def generate(env_path: str, output_path: str, overwrite: bool) -> None:
    """Generate a .env.example from an existing .env file.

    All values are redacted — only key names and comments are preserved.
    """
    generate_example(
        env_path=Path(env_path),
        output_path=Path(output_path),
        overwrite=overwrite,
        console=console,
    )


# ---------------------------------------------------------------------------
# envguard diff
# ---------------------------------------------------------------------------

@main.command()
@click.argument("env_a", type=click.Path(exists=False))
@click.argument("env_b", type=click.Path(exists=False))
def diff(env_a: str, env_b: str) -> None:
    """Show key-level differences between two .env files.

    Only key names are compared — values are never shown.

    \b
    Example:
        envguard diff .env.staging .env.production
    """
    print_diff_report(Path(env_a), Path(env_b), console=console)