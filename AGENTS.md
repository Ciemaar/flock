# Flock Codebase Instructions

This document provides context and guidelines for AI agents working on the Flock codebase.

## Project Overview

Flock is a Python library for managing groups of closures, primarily useful for memorializing mathematical models to allow non-linear execution. It uses a `FlockDict` to encapsulate these closures.

## Tech Stack & Standards

- **Language**: Python 3.10+
- **Build System**: `pyproject.toml` (setuptools backend)
- **Testing**: `pytest`, orchestrated by `tox`.
- **Linting**: `ruff` (line length 160).
- **Type Checking**: `pyright`.
- **CI**: GitHub Actions (Linux & macOS).

## Development Workflow

- **Run all checks**: `tox`
- **Run tests only**: `tox -e py312` (or `pytest` directly if env is set up)
- **Run linting**: `tox -e lint`
- **Run type checking**: `tox -e type`

## Coding Guidelines

1. **No Asserts**: Do not use `assert` in production code (`flock/`, `mythica/`). Use `raise Exception(...)` instead. Asserts are allowed in tests.
1. **Type Safety**: Use type hints. Code must pass `pyright`. Use `cast` or `# type: ignore` sparingly and only when necessary.
1. **Formatting**: Ensure code is formatted with `ruff format`.
1. **Security**: Use safe loading for YAML (`Loader=yaml.Loader` is acceptable for this specific project context per decisions, but prefer `safe_load` where possible). Avoid `pickle` on untrusted data.

## Project Structure

- `flock/`: Core library code.
- `mythica/`: Example/domain implementation utilizing Flock.
- `test/`: Unit and property-based tests (Hypothesis).
- `tox.ini`: Configuration for test environments.
- `.github/workflows/`: CI configuration.
