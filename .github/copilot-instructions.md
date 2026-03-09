# Repository Instructions for GitHub Copilot

These instructions define the coding standards and development workflow for the Flock repository.

## Tech Stack

- **Python**: 3.12, 3.13
- **Build**: `pyproject.toml` using `setuptools`
- **Testing**: `pytest`, `hypothesis`, `tox`
- **Linting/Formatting**: `ruff`
- **Type Checking**: `mypy`

## Coding Standards

- **No Asserts in Production**: Do not use `assert` statements in the source code (`flock/`, `closure_collector/`, `mythica/`). Raise explicit exceptions (e.g., `ValueError`, `TypeError`) instead. `assert` is restricted to the `test/` directory.
- **Type Hints**: All new code should include type hints, but it is preferable to omit type hints entirely rather than using `Any`. The project uses `mypy` for verification.
- **Formatting**: Follow `ruff` formatting rules. Line length is set to 160.
- **Imports**: Imports should be sorted (handled by `ruff`).

## Development Commands

- Run all tests and checks: `tox`
- Run specific python version tests: `tox -e py312`
- Run linting: `tox -e lint`
- Run type checking: `tox -e type`

## CI/CD

- GitHub Actions workflows are located in `.github/workflows/tests.yml`.
- CI runs on Ubuntu and macOS.
