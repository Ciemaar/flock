# Copilot Instructions

*   **Type Hinting in Closure Collector:** When working with `closure_collector` and `flock`, avoid over-typing with `Any`. Prefer omitting type hints if the parameters must accept dynamic values.
*   **Closures:** When creating closures, prefer `lambda: value` over nested `def inner(): return value` statements. This helps the static analysis engine (`mypy`) correctly identify the return types without raising false positives on callable signatures.
*   **Documentation:** All classes, methods, and functions must have meaningful docstrings. Do not use placeholder phrases like "Module providing X".
*   **Tooling:** Ensure you run `ruff check .` and `mypy` to verify changes. `tox` is used for test orchestration. Python versions 3.12 and 3.13 are officially supported.
