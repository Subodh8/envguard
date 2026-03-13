"""Tests for the envguard checker module."""

from pathlib import Path

from envguard.checker import check_env, parse_env_file


# ---------------------------------------------------------------------------
# parse_env_file tests
# ---------------------------------------------------------------------------

class TestParseEnvFile:

    def test_parses_simple_key_value(self, tmp_path: Path) -> None:
        f = tmp_path / ".env"
        f.write_text("DATABASE_URL=postgres://localhost/db\n")
        data, errors = parse_env_file(f)
        assert data == {"DATABASE_URL": "postgres://localhost/db"}
        assert errors == []

    def test_ignores_comments(self, tmp_path: Path) -> None:
        f = tmp_path / ".env"
        f.write_text("# This is a comment\nKEY=value\n")
        data, errors = parse_env_file(f)
        assert "# This is a comment" not in data
        assert data == {"KEY": "value"}

    def test_ignores_blank_lines(self, tmp_path: Path) -> None:
        f = tmp_path / ".env"
        f.write_text("\n\nKEY=value\n\n")
        data, errors = parse_env_file(f)
        assert data == {"KEY": "value"}

    def test_strips_double_quotes(self, tmp_path: Path) -> None:
        f = tmp_path / ".env"
        f.write_text('KEY="my quoted value"\n')
        data, _ = parse_env_file(f)
        assert data["KEY"] == "my quoted value"

    def test_strips_single_quotes(self, tmp_path: Path) -> None:
        f = tmp_path / ".env"
        f.write_text("KEY='my single quoted value'\n")
        data, _ = parse_env_file(f)
        assert data["KEY"] == "my single quoted value"

    def test_handles_export_syntax(self, tmp_path: Path) -> None:
        f = tmp_path / ".env"
        f.write_text("export SECRET=abc123\n")
        data, errors = parse_env_file(f)
        assert data == {"SECRET": "abc123"}
        assert errors == []

    def test_strips_inline_comment(self, tmp_path: Path) -> None:
        f = tmp_path / ".env"
        f.write_text("KEY=value # this is a comment\n")
        data, _ = parse_env_file(f)
        assert data["KEY"] == "value"

    def test_preserves_url_hash(self, tmp_path: Path) -> None:
        """URLs with # in the fragment should not be truncated."""
        f = tmp_path / ".env"
        f.write_text("REDIS_URL=redis://localhost:6379/0\n")
        data, _ = parse_env_file(f)
        assert data["REDIS_URL"] == "redis://localhost:6379/0"

    def test_empty_value(self, tmp_path: Path) -> None:
        f = tmp_path / ".env"
        f.write_text("EMPTY_KEY=\n")
        data, errors = parse_env_file(f)
        assert data["EMPTY_KEY"] == ""
        assert errors == []

    def test_missing_file_returns_error(self, tmp_path: Path) -> None:
        f = tmp_path / "nonexistent.env"
        data, errors = parse_env_file(f)
        assert data == {}
        assert len(errors) == 1
        assert "not found" in errors[0].lower()


# ---------------------------------------------------------------------------
# check_env tests
# ---------------------------------------------------------------------------

class TestCheckEnv:

    def _write(self, tmp_path: Path, name: str, content: str) -> Path:
        f = tmp_path / name
        f.write_text(content)
        return f

    def test_all_keys_present_passes(self, tmp_path: Path) -> None:
        env = self._write(tmp_path, ".env", "A=1\nB=2\n")
        example = self._write(tmp_path, ".env.example", "A=placeholder\nB=placeholder\n")
        result = check_env(env, example)
        assert result.passed
        assert result.missing == []
        assert result.extra == []

    def test_missing_key_detected(self, tmp_path: Path) -> None:
        env = self._write(tmp_path, ".env", "A=1\n")
        example = self._write(tmp_path, ".env.example", "A=placeholder\nB=placeholder\n")
        result = check_env(env, example)
        assert not result.passed
        assert "B" in result.missing

    def test_extra_key_is_warning(self, tmp_path: Path) -> None:
        env = self._write(tmp_path, ".env", "A=1\nZ=extra\n")
        example = self._write(tmp_path, ".env.example", "A=placeholder\n")
        result = check_env(env, example)
        assert result.passed  # extra keys don't fail the check
        assert "Z" in result.extra

    def test_empty_required_key(self, tmp_path: Path) -> None:
        env = self._write(tmp_path, ".env", "SECRET=\n")
        example = self._write(tmp_path, ".env.example", "SECRET=your-secret-here\n")
        result = check_env(env, example)
        assert "SECRET" in result.empty_required

    def test_ignore_keys_skipped(self, tmp_path: Path) -> None:
        env = self._write(tmp_path, ".env", "A=1\n")
        example = self._write(tmp_path, ".env.example", "A=placeholder\nLOCAL_ONLY=\n")
        result = check_env(env, example, ignore_keys=["LOCAL_ONLY"])
        assert "LOCAL_ONLY" not in result.missing
        assert result.passed

    def test_missing_env_file_returns_error(self, tmp_path: Path) -> None:
        env = tmp_path / ".env"
        example = self._write(tmp_path, ".env.example", "A=placeholder\n")
        result = check_env(env, example)
        assert result.errors