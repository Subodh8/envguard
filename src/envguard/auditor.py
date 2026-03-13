"""Secret leak detection for .env files."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from envguard.checker import parse_env_file

# Patterns in KEY NAMES that suggest a value should be secret
SUSPICIOUS_KEY_PATTERNS: list[re.Pattern[str]] = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r"secret",
        r"password",
        r"passwd",
        r"api[_-]?key",
        r"token",
        r"private[_-]?key",
        r"auth[_-]?key",
        r"access[_-]?key",
        r"signing[_-]?key",
        r"encryption[_-]?key",
    ]
]

# Patterns in VALUES that look like real credentials (not placeholders)
CREDENTIAL_VALUE_PATTERNS: list[re.Pattern[str]] = [
    # Generic high-entropy strings (20+ chars of mixed case + digits)
    re.compile(r"^[A-Za-z0-9+/=_\-]{20,}$"),
    # JWT-like (three base64 segments)
    re.compile(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$"),
    # Hex strings (32+ chars)
    re.compile(r"^[0-9a-fA-F]{32,}$"),
]

# Safe placeholder patterns — these look like example values, not real secrets
SAFE_PLACEHOLDER_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"^your[_-]", re.IGNORECASE),
    re.compile(r"^<.+>$"),          # <your-token-here>
    re.compile(r"^\[.+\]$"),        # [REPLACE_ME]
    re.compile(r"^example", re.IGNORECASE),
    re.compile(r"^changeme", re.IGNORECASE),
    re.compile(r"^replace", re.IGNORECASE),
    re.compile(r"^xxx+$", re.IGNORECASE),
]


@dataclass
class AuditFinding:
    """A single suspicious key–value pair."""

    key: str
    reason: str
    severity: str  # "high" | "medium" | "low"


def _looks_like_placeholder(value: str) -> bool:
    return any(p.search(value) for p in SAFE_PLACEHOLDER_PATTERNS)


def _key_is_suspicious(key: str) -> bool:
    return any(p.search(key) for key in [key] for p in SUSPICIOUS_KEY_PATTERNS)


def _value_looks_like_credential(value: str) -> bool:
    if not value or _looks_like_placeholder(value):
        return False
    return any(p.match(value) for p in CREDENTIAL_VALUE_PATTERNS)


def audit_env(env_path: Path) -> list[AuditFinding]:
    """Scan env_path and return a list of suspicious findings.

    Args:
        env_path: Path to the .env file to audit.

    Returns:
        A list of AuditFinding objects, empty if no issues found.
    """
    env_data, errors = parse_env_file(env_path)
    findings: list[AuditFinding] = []

    if errors:
        for err in errors:
            findings.append(AuditFinding(key="[parse error]", reason=err, severity="low"))
        return findings

    for key, value in env_data.items():
        key_suspicious = _key_is_suspicious(key)
        value_suspicious = _value_looks_like_credential(value)

        if key_suspicious and value_suspicious:
            findings.append(
                AuditFinding(
                    key=key,
                    reason="Key name suggests a secret and value looks like a real credential",
                    severity="high",
                )
            )
        elif key_suspicious and value == "":
            # Empty secret key — low risk but worth flagging
            findings.append(
                AuditFinding(
                    key=key,
                    reason="Key name suggests a secret but value is empty",
                    severity="low",
                )
            )
        elif value_suspicious:
            # High-entropy value on a non-secret-named key
            findings.append(
                AuditFinding(
                    key=key,
                    reason="Value looks like a credential (high-entropy string)",
                    severity="medium",
                )
            )

    return findings