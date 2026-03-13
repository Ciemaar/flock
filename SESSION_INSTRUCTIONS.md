# Session Instructions and Guidelines

During this development session, several key architectural, tooling, and stylistic decisions were made and enforced. These guidelines should inform future work in this repository:

## 1. Tooling and Linting

*   **Ruff:** We use `ruff` as our primary linter and formatter. Auto-generated or placeholder docstrings (e.g., `"""Module providing X implementation."""` or `"""Execute the Y operation."""`) are strictly prohibited, as they trigger reviewer rejections. All `ruff` `D` checks (docstrings) must be satisfied with **meaningful, context-aware descriptions**.
*   **Mypy:** We use `mypy` for static type checking. Due to the highly dynamic and metaprogramming-heavy nature of `closure_collector`, `mypy` is currently preferred over `pyright` as it correctly evaluates duck typing, callable interfaces, and default values without emitting false positive errors or requiring blanket `Any` suppressions.
*   **Markdown Formatting:** All markdown files must be formatted with `mdformat`.
*   **Tox:** We use `tox` for cross-version testing and CI orchestration. `tox.ini` has been integrated into `pyproject.toml` via `legacy_tox_ini`.

## 2. Type Hinting in Closure Collector

Type hinting within `closure_collector` and `flock` requires a specific approach due to the reliance on parameter inspection and closures:

*   **Avoid Over-Typing with `Any`:** Prefer omitting type hints altogether rather than applying `Any` to parameters that accept dynamic values.
*   **Prefer Lambdas over Local `def`s:** When creating closures, `lambda: value` is preferred over `def inner(): return value`. Some type checkers (like `pyright`) misinterpret local `def` closures and inject `Any` return types incorrectly, whereas `lambda` statements bypass this static analysis quirk.
*   **Callable and Dict:** Use `typing.Mapping` and `typing.Callable` appropriately to represent the dictionaries and rule functions processed by the collectors.

## 3. Architecture

*   The core functionality of `flock` has been refactored and generalized into a standalone library called `closure_collector`.
*   The `flock` module now serves primarily as a backward-compatibility wrapper (`FlockDict` built on `DynamicClosureCollector`). New functionality should target `closure_collector`.
*   `examples/mythica/model.py` demonstrates a real-world use case for `closure_collector` rules and should be kept functional and lint-free as an integration test.

## 4. Workflows

*   The CI is defined in `.github/workflows/tests.yml` and utilizes `tox` across Python 3.9, 3.10, 3.11, 3.12, and 3.13.
*   Before submission, all tests must pass locally: `tox -e py312,lint,type`.
