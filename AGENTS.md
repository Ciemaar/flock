# Flock / Closure Collector Codebase Instructions

This document provides context and guidelines for AI agents working on the Flock / Closure Collector codebase.

## Project Overview

Flock/Closure Collector is a Python library for managing groups of closures, primarily useful for memorializing
mathematical models to allow non-linear execution. It uses a `FlockDict` to encapsulate these closures.

## Tech Stack & Standards

- **Language**: Python 3.12, 3.13
- **Build System**: `pyproject.toml` (setuptools backend)
- **Testing**: `pytest`, orchestrated by `tox`.
- **Linting**: `ruff` (line length 160).
- **Type Checking**: `mypy`.
- **CI**: GitHub Actions (Linux & macOS).

## Development Workflow

- **Run all checks**: `tox`
- **Run tests only**: `tox -e py312` (or `pytest` directly if env is set up)
- **Run linting**: `tox -e lint`
- **Run type checking**: `tox -e type`

## Coding Guidelines

1. **No Asserts**: Do not use `assert` in production code (`flock/`, `closure_collector/`, `mythica/`). Use
   `raise Exception(...)` instead. Asserts are allowed in tests.
1. **Formatting**: Ensure code is formatted with `ruff format`.
1. **Type Safety**: Use type hints. Code must pass `mypy`. However, **due to the heavy metaprogramming and dynamic
   duck-typing nature of `closure_collector`, type hinting is highly complex**.
    - It is preferable to omit type hints entirely rather than using `Any`.
    - Do not aggressively type-hint dynamic variables or try to force strict structural interfaces on components
      designed to morph at runtime.
    - If `mypy` flags a dynamic evaluation pattern that is verifiably correct at runtime, use a targeted
      `# type: ignore` comment rather than altering the dynamic logic.
1. **Security**: Use safe loading for YAML (`Loader=yaml.Loader` is acceptable for this specific project context per
   decisions, but prefer `safe_load` where possible). Avoid `pickle` on untrusted data.

## Project Structure

- `closure_collector/`: Core library code.
- `flock/`: Compatibility wrapper.
- `examples/mythica/`: Example/domain implementation utilizing closures.
- `test/`: Unit and property-based tests (Hypothesis).
- `tox.ini`: Configuration for test environments.
- `.github/workflows/`: CI configuration.
