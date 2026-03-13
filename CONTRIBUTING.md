# Contributing to EnvGuard

First of all: thank you for considering a contribution! EnvGuard is designed to be
beginner-friendly, and we genuinely want to help you make your first open-source contribution.

## Where to start

Browse our [good first issues](https://github.com/your-username/envguard/labels/good%20first%20issue) —
these are specifically scoped to be completable in an evening without deep knowledge of the codebase.

## Setting up your development environment
```bash
# 1. Fork the repo on GitHub, then clone your fork
git clone https://github.com/YOUR-USERNAME/envguard.git
cd envguard

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install the package in editable mode with dev tools
pip install -e ".[dev]"

# 4. Install pre-commit hooks (runs linting automatically before each commit)
pre-commit install

# 5. Verify everything works
pytest
```

## Project structure quick tour

| Path | What lives there |
|---|---|
| `src/envguard/checker.py` | Parsing .env files and comparing keys |
| `src/envguard/auditor.py` | Secret pattern detection |
| `src/envguard/generator.py` | Creating .env.example files |
| `src/envguard/reporter.py` | All terminal output (Rich formatting) |
| `src/envguard/cli.py` | Click CLI wiring — calls the above modules |
| `tests/` | Pytest test suite — mirror of the src structure |

The best place to start reading is `checker.py` — it's the core and the most commented.

## Making a change
```bash
# Create a branch for your work
git checkout -b fix/my-descriptive-branch-name

# Make your changes, then run the test suite
pytest

# Check for lint errors
ruff check src tests

# Stage and commit
git add .
git commit -m "fix: describe what you changed in present tense"

# Push and open a PR
git push origin fix/my-descriptive-branch-name
```

## Commit message style

We follow [Conventional Commits](https://www.conventionalcommits.org/):
```
feat: add support for YAML config files
fix: handle BOM character at start of .env file
docs: clarify --fail-on-warning behaviour in README
test: add edge case for empty .env.example
refactor: extract _parse_line into its own function
```

## Adding a new secret pattern

A great first contribution is adding a new pattern to `auditor.py`:

1. Open `src/envguard/auditor.py`
2. Add your regex to `SUSPICIOUS_KEY_PATTERNS` or `CREDENTIAL_VALUE_PATTERNS`
3. Add a test in `tests/test_auditor.py` — one test for true positive, one for false positive
4. Submit your PR with a comment explaining why the pattern is useful

## Running specific tests
```bash
pytest tests/test_checker.py                         # single file
pytest tests/test_checker.py::TestCheckEnv           # single class
pytest tests/test_checker.py::TestCheckEnv::test_missing_key_detected  # single test
pytest -v                                            # verbose output
pytest --tb=short                                    # shorter tracebacks
```

## Code style

- We use [Ruff](https://docs.astral.sh/ruff/) for formatting and linting — it runs automatically via pre-commit
- Type annotations are required on all public functions
- Docstrings follow Google style

## Questions?

Open a [Discussion](https://github.com/your-username/envguard/discussions) — we're happy to help you
get unstuck or talk through an idea before you write code.