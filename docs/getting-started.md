# Getting started with EnvGuard

## Installation
```bash
pip install envguard
```

## Your first check

Navigate to any project that has a `.env` and `.env.example` file:
```bash
cd my-project
envguard check
```

If your project only has a `.env` (no `.env.example`), generate one first:
```bash
envguard generate
# Creates .env.example with all values redacted — safe to commit
```

## Using in CI

Add this to your GitHub Actions workflow to catch config drift in PRs:
```yaml
- name: Validate environment config
  run: envguard check --format json
```

The `--format json` flag makes the output machine-readable and easy to parse in scripts.

## Using as a pre-commit hook
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/your-username/envguard
    rev: v0.1.0
    hooks:
      - id: envguard-check
```

## Configuration reference

| Key | Default | Description |
|---|---|---|
| `env_file` | `.env` | Path to your env file |
| `example_file` | `.env.example` | Path to the template |
| `ignore_keys` | `[]` | Keys to skip during validation |
| `fail_on_warning` | `false` | Treat undocumented keys as errors |