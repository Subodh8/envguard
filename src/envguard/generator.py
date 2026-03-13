"""Generate .env.example files from existing .env files."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console


def generate_example(
    env_path: Path,
    output_path: Path,
    overwrite: bool = False,
    console: Console | None = None,
) -> None:
    """Generate a .env.example from an existing .env file.

    All values are redacted. Comments and blank lines are preserved.
    The resulting file is safe to commit to version control.

    Args:
        env_path: Source .env file to read.
        output_path: Destination path for the generated .env.example.
        overwrite: If False and output_path exists, raise an error.
        console: Rich console for output. Uses a default console if None.
    """
    _console = console or Console()

    if not env_path.exists():
        _console.print(f"[red]✗[/red] Source file not found: {env_path}")
        return

    if output_path.exists() and not overwrite:
        _console.print(
            f"[yellow]⚠[/yellow] {output_path} already exists. "
            "Use --overwrite to replace it."
        )
        return

    lines = env_path.read_text(encoding="utf-8").splitlines(keepends=True)
    output_lines: list[str] = []
    redacted_count = 0

    for raw_line in lines:
        line = raw_line.strip()

        # Preserve blank lines and comments as-is
        if not line or line.startswith("#"):
            output_lines.append(raw_line)
            continue

        # Handle `export KEY=VALUE`
        prefix = ""
        if line.startswith("export "):
            prefix = "export "
            line = line[len("export "):].strip()

        if "=" not in line:
            output_lines.append(raw_line)
            continue

        key, _, _ = line.partition("=")
        key = key.strip()

        # Write key with empty value
        output_lines.append(f"{prefix}{key}=\n")
        redacted_count += 1

    output_path.write_text("".join(output_lines), encoding="utf-8")

    _console.print(
        f"[green]✔[/green] Generated [bold]{output_path}[/bold] "
        f"({redacted_count} keys, all values redacted)"
    )