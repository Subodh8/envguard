# Changelog

All notable changes to EnvGuard are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

_(Add your changes here — they'll be moved to the next release section)_

---

## [0.1.0] — 2024-01-15

### Added
- `envguard check` command — validates .env against .env.example
- `envguard audit` command — scans for potential secret leaks
- `envguard generate` command — creates .env.example from .env
- `envguard diff` command — key-level diff between two env files
- `--format json` flag on `check` and `audit` for CI pipeline integration
- `--fail-on-warning` flag on `check`
- Rich terminal output with colour-coded results
- Pre-commit hook support
- Python 3.9–3.12 support