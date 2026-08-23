# Repository Instructions for GitHub Copilot

These instructions define the coding standards and development workflow for the Flock repository.

## Project Overview & Architecture

- **Purpose**: Flock/Closure Collector is a Python library for managing groups of closures, primarily useful for memorializing mathematical models to allow non-linear execution.
- **Layers**:
  - `closure_collector/`: Core library logic.
  - `flock/`: Compatibility wrapper acting as a backward compatibility layer built on top of `closure_collector`. `flock` objects should be implemented by inheriting from or wrapping core `closure_collector` objects.
  - `mythica/`: Sample domain implementations.
  - `examples/`: Usage examples.
  - `test/`: Unit and property-based tests (Hypothesis).
- **Public API**: Users of the `flock` layer primarily interact with leaf-classes (`FlockDict`, `FlockList`, `FlockAggregator`, `PromiseFlock`).
- **Default Branch**: The repository's default branch is `master`, not `main`.

## Tech Stack & Tooling

- **Python**: 3.12, 3.13
- **Build**: `pyproject.toml` using `setuptools`
- **Testing**: `pytest`, `hypothesis`, `tox`
- **Linting/Formatting**: `ruff`, `mdformat`
- **Type Checking**: `mypy`

## Coding Standards

- **No Asserts in Production**: Do not use `assert` statements in the source code (`flock/`, `closure_collector/`, `mythica/`, `examples/`). Raise explicit exceptions (e.g., `ValueError`, `TypeError`) instead. `assert` is restricted to the `test/` directory, with the specific exception of `assert callable(...)` checks, which are permitted in production code.
- **Formatting**: Follow `ruff` formatting rules. Line length is set to 160. Adopt modern Python paradigms (e.g., using `|` for union types instead of `(A, B)` in `isinstance` checks).
- **Docstrings**: All classes, methods, and functions must have meaningful docstrings. Must be placed as the absolute first statement in a method or class body. Do not use placeholder phrases like "Module providing X".
- **Default Arguments**: Avoid using mutable default arguments (e.g., `[]`, `{}`) in function signatures. Use `None` as the default value instead.
- **Performance Optimizations**:
  - Pre-evaluate combined valid keys into a tuple (e.g., `valid_keys = tuple(set().union(...))`) and invert nested loops to iterate over sources first, then keys.
  - Prefer using generator comprehensions (e.g., `*(x for x in ...)` ) over list comprehensions (e.g., `*[x for x in ...]`) when unpacking collections.
- **Closures:** When creating closures, prefer `lambda: value` over nested `def inner(): return value` statements. This helps the static analysis engine (`mypy`) correctly identify the return types without raising false positives on callable signatures.

## Type Hinting

- **Type Hinting Complexities:** Because this project relies heavily on dynamic metaprogramming and runtime duck-typing, type hinting is highly complex.
- **Omissions Over `Any`:** Prefer to omit type hints entirely rather than using `Any`. Do not aggressively type-hint dynamic variables or try to force strict structural interfaces.
- **Targeted `# type: ignore`:** If `mypy` flags a dynamic evaluation pattern that is verifiably correct at runtime, use a targeted `# type: ignore` comment.
- **Variable Initialization**: When initializing empty collections or using `defaultdict`, provide explicit type annotations for the variable (e.g., `ret: dict = defaultdict(dict)`).

## Development Commands

- Run all tests and checks: `tox`
- Run specific python version tests: `tox -e py312`
- Run linting: `tox -e lint`
- Run type checking: `tox -e type`

## Branch Management & PRs

- When working on an existing, previous branch (e.g., rebasing or merging), features must not be removed if they have been added to the main branch in the intermediate interval.
- All branches being merged in, as well as their matching PRs, must be referenced in the commit comments and any new PRs.

## CI/CD

- GitHub Actions workflows are located in `.github/workflows/tests.yml`.
- CI runs on push to any branch, pull requests to main/master, and manual dispatch.
