"""Core .env validation logic."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class CheckResult:
    """Holds the outcome of a single check run."""

    env_path: Path
    example_path: Path
    # Keys in .env.example but not in .env
    missing: list[str] = field(default_factory=list)
    # Keys in .env but not in .env.example
    extra: list[str] = field(default_factory=list)
    # Keys present but with empty values when example has a value hint
    empty_required: list[str] = field(default_factory=list)
    # Keys present and correctly populated
    ok: list[str] = field(default_factory=list)
    # Error loading files
    errors: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """True when no errors were found."""
        return not (self.missing or self.empty_required or self.errors)

    @property
    def summary(self) -> str:
        n_err = len(self.missing) + len(self.empty_required)
        n_warn = len(self.extra)
        if n_err == 0 and n_warn == 0:
            return "All checks passed"
        parts = []
        if n_err:
            parts.append(f"{n_err} error{'s' if n_err != 1 else ''}")
        if n_warn:
            parts.append(f"{n_warn} warning{'s' if n_warn != 1 else ''}")
        return ", ".join(parts)


def parse_env_file(path: Path) -> tuple[dict[str, str], list[str]]:
    """Parse a .env file into a key→value dict.

    Returns:
        A tuple of (key_value_dict, list_of_errors).

    Handles:
        - Comments (lines starting with #)
        - Blank lines
        - KEY=VALUE pairs
        - Quoted values ("value" or 'value')
        - Inline comments (KEY=VALUE  # comment)
        - export KEY=VALUE syntax
    """
    result: dict[str, str] = {}
    errors: list[str] = []

    if not path.exists():
        errors.append(f"File not found: {path}")
        return result, errors

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"Cannot read {path}: {exc}")
        return result, errors

    for lineno, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()

        # Skip blank lines and comments
        if not line or line.startswith("#"):
            continue

        # Handle `export KEY=VALUE` syntax
        if line.startswith("export "):
            line = line[len("export "):].strip()

        if "=" not in line:
            errors.append(f"Line {lineno}: no '=' found — skipping: {raw_line!r}")
            continue

        key, _, raw_value = line.partition("=")
        key = key.strip()

        if not key:
            errors.append(f"Line {lineno}: empty key — skipping.")
            continue

        value = _strip_inline_comment(_unquote(raw_value.strip()))
        result[key] = value

    return result, errors


def _unquote(value: str) -> str:
    """Remove surrounding quotes from a value."""
    if len(value) >= 2:
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            return value[1:-1]
    return value


def _strip_inline_comment(value: str) -> str:
    """Remove trailing inline comment (e.g. VALUE  # comment → VALUE)."""
    # Only strip if there's a space before the #, to avoid stripping URLs
    if " #" in value:
        value = value[: value.index(" #")].rstrip()
    return value


def check_env(
    env_path: Path = Path(".env"),
    example_path: Path = Path(".env.example"),
    ignore_keys: Optional[list[str]] = None,
) -> CheckResult:
    """Validate env_path against example_path.

    Args:
        env_path: The actual .env file to validate.
        example_path: The .env.example acting as the required-keys template.
        ignore_keys: Keys to skip during validation.

    Returns:
        A CheckResult dataclass with categorised keys.
    """
    result = CheckResult(env_path=env_path, example_path=example_path)
    ignore = set(ignore_keys or [])

    env_data, env_errors = parse_env_file(env_path)
    example_data, example_errors = parse_env_file(example_path)

    result.errors.extend(env_errors)
    result.errors.extend(example_errors)

    if result.errors:
        return result

    env_keys = set(env_data.keys()) - ignore
    example_keys = set(example_data.keys()) - ignore

    # Keys in example but absent from .env → hard errors
    for key in sorted(example_keys - env_keys):
        result.missing.append(key)

    # Keys in .env but not documented in example → warnings
    for key in sorted(env_keys - example_keys):
        result.extra.append(key)

    # Keys present in both — check for empty values
    for key in sorted(env_keys & example_keys):
        if env_data[key] == "" and example_data[key] != "":
            # Example has a placeholder but .env is empty
            result.empty_required.append(key)
        else:
            result.ok.append(key)

    return result