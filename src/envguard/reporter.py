"""Terminal output formatting for EnvGuard."""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

from envguard.auditor import AuditFinding
from envguard.checker import CheckResult, parse_env_file

SEVERITY_COLOUR = {"high": "red", "medium": "yellow", "low": "blue"}
SEVERITY_ICON = {"high": "✗", "medium": "⚠", "low": "ℹ"}


def print_check_report(
    result: CheckResult,
    output_format: str = "text",
    console: Console | None = None,
) -> None:
    _console = console or Console()

    if output_format == "json":
        _console.print(
            json.dumps(
                {
                    "env": str(result.env_path),
                    "example": str(result.example_path),
                    "missing": result.missing,
                    "extra": result.extra,
                    "empty_required": result.empty_required,
                    "ok": result.ok,
                    "passed": result.passed,
                    "summary": result.summary,
                },
                indent=2,
            )
        )
        return

    if result.errors:
        for err in result.errors:
            _console.print(f"[red]Error:[/red] {err}")
        return

    _console.print(f"\nChecking [bold]{result.env_path}[/bold] against [bold]{result.example_path}[/bold]\n")

    for key in result.ok:
        _console.print(f"  [green]✔[/green]  {key}")

    for key in result.missing:
        _console.print(f"  [red]✗[/red]  {key}  [dim]missing from .env (required by .env.example)[/dim]")

    for key in result.empty_required:
        _console.print(f"  [yellow]⚠[/yellow]  {key}  [dim]empty value — required key has no value[/dim]")

    for key in result.extra:
        _console.print(f"  [blue]ℹ[/blue]  {key}  [dim]present in .env but not in .env.example (undocumented)[/dim]")

    colour = "green" if result.passed else "red"
    _console.print(f"\n[{colour}]{result.summary}[/{colour}]\n")


def print_audit_report(
    findings: list[AuditFinding],
    output_format: str = "text",
    console: Console | None = None,
) -> None:
    _console = console or Console()

    if output_format == "json":
        _console.print(
            json.dumps(
                [{"key": f.key, "reason": f.reason, "severity": f.severity} for f in findings],
                indent=2,
            )
        )
        return

    if not findings:
        _console.print("[green]✔[/green] No suspicious patterns found.")
        return

    table = Table(title="Audit findings", show_header=True, header_style="bold")
    table.add_column("Severity", style="bold", width=10)
    table.add_column("Key", width=30)
    table.add_column("Reason")

    for f in findings:
        colour = SEVERITY_COLOUR.get(f.severity, "white")
        icon = SEVERITY_ICON.get(f.severity, "?")
        table.add_row(
            f"[{colour}]{icon} {f.severity.upper()}[/{colour}]",
            f.key,
            f.reason,
        )

    _console.print(table)


def print_diff_report(
    env_a: Path,
    env_b: Path,
    console: Console | None = None,
) -> None:
    _console = console or Console()

    data_a, errs_a = parse_env_file(env_a)
    data_b, errs_b = parse_env_file(env_b)

    for err in errs_a + errs_b:
        _console.print(f"[red]Error:[/red] {err}")

    if errs_a or errs_b:
        return

    keys_a = set(data_a)
    keys_b = set(data_b)
    all_keys = sorted(keys_a | keys_b)

    _console.print(f"\nDiff: [bold]{env_a}[/bold] vs [bold]{env_b}[/bold]\n")

    any_diff = False
    for key in all_keys:
        if key in keys_a and key not in keys_b:
            _console.print(f"  [red]−[/red]  {key}  [dim]only in {env_a.name}[/dim]")
            any_diff = True
        elif key in keys_b and key not in keys_a:
            _console.print(f"  [green]+[/green]  {key}  [dim]only in {env_b.name}[/dim]")
            any_diff = True
        else:
            # Key present in both — note if one is empty and the other isn't
            a_empty = data_a[key] == ""
            b_empty = data_b[key] == ""
            if a_empty != b_empty:
                status = f"{env_a.name}: {'empty' if a_empty else 'set'}, {env_b.name}: {'empty' if b_empty else 'set'}"
                _console.print(f"  [yellow]~[/yellow]  {key}  [dim]{status}[/dim]")
                any_diff = True

    if not any_diff:
        _console.print("[green]✔[/green] No key-level differences found.\n")
    else:
        _console.print()