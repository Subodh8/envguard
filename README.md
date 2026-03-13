# EnvGuard 🛡️

**Never ship broken environment configs again.**

EnvGuard is a developer CLI tool that validates, audits, and generates `.env` files — catching
missing keys, leaked secrets, and configuration drift before they reach production.

[![CI](https://github.com/Subodh8/envguard/actions/workflows/ci.yml/badge.svg)](https://github.com/Subodh8/envguard/actions)
[![PyPI version](https://badge.fury.io/py/envguard.svg)](https://badge.fury.io/py/envguard)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## The problem

You've been there. A teammate pushes a change. The deploy fails. Turns out their `.env.example`
was out of date and three required variables were never documented. EnvGuard fixes this.

## Features

| Command | What it does |
|---|---|
| `envguard check` | Validate `.env` against `.env.example` — find missing or undocumented keys |
| `envguard audit` | Scan for potential secret leaks (raw tokens, passwords, API keys) |
| `envguard generate` | Auto-create a safe `.env.example` from your `.env` (values redacted) |
| `envguard diff` | Show what changed between two `.env` files |

## Quick start
```bash
pip install envguard
cd your-project
envguard check
```

### Example output
```
✔  DATABASE_URL        present
✔  REDIS_URL           present
✗  STRIPE_SECRET_KEY   missing from .env (defined in .env.example)
⚠  JWT_SECRET          empty value — required key has no value
⚠  OLD_API_TOKEN       present in .env but not in .env.example (undocumented)

Summary: 2 errors, 1 warning  ← fix these before deploying
```

## Installation
```bash
# From PyPI
pip install envguard

# From source (for development)
git clone https://github.com/Subodh8/envguard.git
cd envguard
pip install -e ".[dev]"
```

## Usage
```bash
# Check .env against .env.example (defaults)
envguard check

# Specify custom paths
envguard check --env .env.production --example .env.example

# Audit for exposed secrets
envguard audit --env .env

# Generate .env.example from existing .env
envguard generate --env .env --output .env.example

# Diff two env files
envguard diff .env.staging .env.production

# Output as JSON (for CI pipelines)
envguard check --format json
```

## Pre-commit hook

Add EnvGuard to your pre-commit pipeline so it runs automatically on every commit:
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/Subodh8/envguard
    rev: v0.1.0
    hooks:
      - id: envguard-check
```

Then install the hook:
```bash
pip install pre-commit
pre-commit install
```

## Configuration

Create an `envguard.toml` in your project root to customise behaviour:
```toml
[envguard]
env_file = ".env"
example_file = ".env.example"
ignore_keys = ["LOCAL_OVERRIDE", "DEBUG"]
secret_patterns = ["TOKEN", "SECRET", "PASSWORD", "API_KEY"]
fail_on_warning = false
```

## Contributing

We love contributions! EnvGuard is beginner-friendly by design — see [CONTRIBUTING.md](CONTRIBUTING.md)
for a guided walkthrough. Check the [good first issues](https://github.com/Subodh8/envguard/labels/good%20first%20issue)
label to get started.

## License

MIT — see [LICENSE](LICENSE).