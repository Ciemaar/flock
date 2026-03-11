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
- **Formatting**: Follow `ruff` formatting rules. Line length is set to 160.
- **Type Hints**: Because this project relies heavily on dynamic metaprogramming and runtime duck-typing, type hinting is highly complex. Prefer to omit type hints entirely rather than using `Any`. Do not aggressively type-hint dynamic variables or try to force strict structural interfaces. If `mypy` flags a dynamic evaluation pattern that is verifiably correct at runtime, use a targeted `# type: ignore` comment.
- **Imports**: Imports should be sorted (handled by `ruff`).

## Development Commands

- Run all tests and checks: `tox`
- Run specific python version tests: `tox -e py312`
- Run linting: `tox -e lint`
- Run type checking: `tox -e type`

## CI/CD

- GitHub Actions workflows are located in `.github/workflows/tests.yml`.
- CI runs on Ubuntu and macOS.
