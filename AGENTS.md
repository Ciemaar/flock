# Flock / Closure Collector Codebase Instructions

This document provides context and guidelines for AI agents working on the Flock / Closure Collector codebase. It consolidates all guidelines, testing strategies, coding standards, and memory states for developers and agents interacting with this repository.

## Project Overview & Architecture

- **Purpose**: Flock/Closure Collector is a Python library for managing groups of closures, primarily useful for memorializing mathematical models to allow non-linear execution.
- **Layers**:
  - `closure_collector/`: Core library logic.
  - `flock/`: Compatibility wrapper acting as a backward compatibility layer built on top of `closure_collector`. `flock` objects (e.g., `FlockDict`, `FlockList`, `FlockAggregator`) should be implemented by inheriting from or wrapping core `closure_collector` objects (e.g., `ClosureMapping`, `ClosureList`) to provide their interface.
  - `mythica/`: Sample domain implementations.
  - `examples/`: Usage examples.
  - `test/`: Unit and property-based tests (Hypothesis).
- **Public API**: Users of the `flock` layer primarily interact with leaf-classes in the inheritance hierarchy, specifically `FlockDict`, `FlockList`, `FlockAggregator`, and `PromiseFlock`. Abstract or intermediate base classes can be aggressively pruned if orphaned.
- **AI Instructions**: AI agent instructions are maintained in this `AGENTS.md` (root) file, and `.github/copilot-instructions.md` (for GitHub Copilot and JetBrains IDEs).
- **Default Branch**: The repository's default branch is `master`, not `main`.

## Tech Stack & Tooling

- **Language**: Python 3.12, 3.13 (Python 3.12 or later is required).
- **Build System & Configuration**: All build (`setuptools`) and tool configuration, including `tox` (via `legacy_tox_ini`), `ruff`, `mypy`, and `pytest`, is centrally managed in `pyproject.toml`.
- **Dependencies**: `PyYAML`, `pydantic-settings`, `click`, and `glom`.
  - Optional dependencies in `pyproject.toml`: `test` (`pytest`, `hypothesis`, `pytest-cov`, `coverage`), `dev` (`ruff`, `mypy`, `mdformat`, `tox`) allow developers to easily install all required tooling.
- **Data Access Tooling**: `glom` for resilient, declarative nested data access. When using `glom`, prefer native spec primitives like `glom.T` or `glom.Path` for dynamic item/attribute access rather than using custom callables or undocumented kwargs like `skip_exc`. This ensures correct exception wrapping (`PathAccessError`) and reliable `default` fallback behaviors.
- **Linting & Formatting**:
  - `ruff` (line length 160). Enforces standard checks including `UP` (pyupgrade) rules, `B` (flake8-bugbear) rules, missing docstrings (`D` pydocstyle rules) using the "google" convention. Ignores subjective formatting rules (e.g., `D203`, `D212`) and the `test/` directory.
  - `mdformat` is used to check and format Markdown files, integrated into the `tox` lint environment. It requires explicit paths (e.g., `README.md AGENTS.md TOOLING_EVALUATION.md .github flock closure_collector examples`) to prevent checking files in `.tox` or other ignored directories.
- **Type Checking**: `mypy`. Used natively because it handles dynamic metaprogramming and duck-typing abstractions in `closure_collector` without requiring global structural type suppressions.
- **CI**: GitHub Actions is configured (`.github/workflows/tests.yml`) to run tests on push to any branch, pull requests to main/master, and manual dispatch.

## Testing & Environments

- **Tox Environment**: Orchestrates testing and linting environments.
  - `tox -e py312` (or `py313`): Execute test suites.
  - `tox -e lint`: Run code formatting checks (`ruff` and `mdformat`).
  - `tox -e type`: Run static type checking (`mypy`).
  - To run a specific test file using `tox` with `pytest` arguments, pass the file path after a double dash (e.g., `tox -e py312 -- test/test_flockdict.py`).
- **MicroPython Environment**: Supported. MicroPython tests are executed using a tailored test runner script, `run_micropython_tests.py`, which is configured and invoked within the `tox` environment. Missing standard modules (e.g., `typing`, `inspect`, `abc`) must be centrally managed in `compat.py` modules (e.g., `src/closure_collector/compat.py` and `src/flock/compat.py`) rather than written inline.
- **Pyodide Environment**: Supported. Pyodide compatibility tests are executed via `tox -e pyodide` using the `pytest-pyodide` dependency and the `pytest test/ --run-in-pyodide` command.

## Coding Standards

- **No Asserts in Production**: Do not use `assert` statements in production code (`flock/`, `closure_collector/`, `mythica/`, `examples/`). Raise explicit exceptions instead. `assert` is restricted to the `test/` directory, with the specific exception of `assert callable(...)` checks, which are permitted in production code.
- **Docstrings**: All classes, methods, and functions must have meaningful docstrings. Must be placed as the absolute first statement in a method or class body, preceding any logic, assertions, or variable assignments.
- **Default Arguments**: Avoid using mutable default arguments (e.g., `[]`, `{}`) in function signatures. Use `None` as the default value instead and initialize the mutable object inside the function (e.g., `if path is None: path = []`), updating docstrings and type hints (using `| None`) to reflect the change.
- **Performance Optimizations**:
  - When checking or aggregating across multiple mapping sources, pre-evaluate combined valid keys into a tuple (e.g., `valid_keys = tuple(set().union(...))`) and invert nested loops to iterate over sources first, then keys. This avoids redundant scanning and method calls.
  - When unpacking collections for operations like `set().union()`, prefer using generator comprehensions (e.g., `*(x for x in ...)` ) over list comprehensions (e.g., `*[x for x in ...]`) to minimize memory overhead.
- **Clean Code**: Generally remove dead or commented-out code methods unless there is a documented reason to keep them.
- **Modern Python Paradigms**: Adopt modern Python paradigms (e.g., using `|` for union types instead of `(A, B)` in `isinstance` checks).

## Type Hinting Complexities

- **Dynamic Typing Context**: Type hinting in this project is exceptionally complex due to dynamic metaprogramming, runtime duck-typing, and inspection of underlying `__closure__` cells. Developers should avoid aggressively type-hinting dynamic variables.
- **Omissions Over `Any`**: When writing type hints, it is preferable to omit type hints entirely rather than using the `Any` type.
- **Targeted `# type: ignore`**: If `mypy` flags a dynamic evaluation pattern that is verifiably correct at runtime, use a targeted `# type: ignore` comment rather than altering the dynamic logic.
- **Variable Initialization**: When initializing empty collections or using `defaultdict`, provide explicit type annotations for the variable (e.g., `ret: dict = defaultdict(dict)`) to prevent `mypy` 'Need type annotation' errors.
- **Modifying Files**: When making changes, limit docstring and typing updates strictly to the specific locations or classes being modified rather than updating entire files unnecessarily.

## Pull Requests, Workflows, and Agents

- **Code Health PRs**: When creating a PR for code health improvements, use the title format '🧹 [code health improvement description]' and include the following sections in the description: '🎯 What', '💡 Why', '✅ Verification', and '✨ Result'. Always preserve functionality over cleanliness.
- **Branches and Merging**: When working on an existing branch (e.g., rebasing or merging) or consolidating previous work, features added to the main branch in the intermediate interval must not be removed. All merged branches and their matching PR numbers must be explicitly referenced in commit comments and any new PR descriptions for traceability.
- **Agent Deep Planning Mode**: Agents should always ask clarifying questions using `request_user_input` or `message_user` to verify assumptions before creating a plan, even if the task seems clear. Do not ask questions that can be derived from the code. Create a plan using `set_plan` only when absolutely certain. After the plan is approved, execute it autonomously without asking for further confirmation.
