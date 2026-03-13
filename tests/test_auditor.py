"""Tests for the envguard auditor module."""

from pathlib import Path

from envguard.auditor import audit_env


class TestAuditEnv:

    def _write(self, tmp_path: Path, content: str) -> Path:
        f = tmp_path / ".env"
        f.write_text(content)
        return f

    def test_clean_file_has_no_findings(self, tmp_path: Path) -> None:
        f = self._write(tmp_path, "DATABASE_URL=postgres://localhost/db\nDEBUG=true\n")
        findings = audit_env(f)
        assert findings == []

    def test_detects_high_entropy_secret(self, tmp_path: Path) -> None:
        f = self._write(
            tmp_path,
            "API_SECRET=sk-abcdefghijklmnopqrstuvwxyz123456\n",
        )
        findings = audit_env(f)
        assert any(f.severity == "high" for f in findings)
        assert any(f.key == "API_SECRET" for f in findings)

    def test_placeholder_not_flagged(self, tmp_path: Path) -> None:
        f = self._write(tmp_path, "API_KEY=your-api-key-here\n")
        findings = audit_env(f)
        # Placeholder values should not trigger high-severity findings
        high = [f for f in findings if f.severity == "high"]
        assert high == []

    def test_empty_secret_key_is_low(self, tmp_path: Path) -> None:
        f = self._write(tmp_path, "JWT_SECRET=\n")
        findings = audit_env(f)
        assert any(f.severity == "low" and f.key == "JWT_SECRET" for f in findings)

    def test_missing_file_returns_error_finding(self, tmp_path: Path) -> None:
        f = tmp_path / "nonexistent.env"
        findings = audit_env(f)
        assert findings
        assert findings[0].key == "[parse error]"