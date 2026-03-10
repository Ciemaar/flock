# Tooling Evaluation Notes

This document captures the rationale behind the selected development tools for the `closure_collector` (formerly `flock`) repository. Given the project's heavy reliance on dynamic metaprogramming (intercepting `__closure__` variables, deep duck-typing of collections), certain tools perform significantly better than others.

## Formatting & Linting

### Candidates:

1. **Ruff** (Selected)
1. **Black + Flake8**
1. **Pylint**

### Evaluation:

- **Ruff** was selected as the unified formatting and linting tool. It replaces dozens of legacy plugins (like `flake8-docstrings`, `bandit`, `isort`) with a single, blazing-fast Rust-based binary.
- It allows us to easily enforce `pydocstyle` (missing docstrings) without failing on subjective formatting rules (e.g., `D203`).
- **Black + Flake8** is the traditional standard, but managing multiple configurations and slower execution times makes it less desirable than Ruff for a modern Python 3.12+ project.
- **Pylint** is highly configurable but notorious for false positives, particularly in codebases doing heavy metaclass manipulation or dynamic attribute assignment (like `DynamicClosureCollector`). Ruff's static analysis is less noisy for this specific architecture.

## Static Type Checking

### Candidates:

1. **MyPy** (Selected)
1. **Pyright**

### Evaluation:

- **Pyright** was initially tested. However, Pyright enforces a very strict structural type system that fundamentally clashes with how `closure_collector` works. Specifically, the dynamic inspection of `value.__closure__` and the duck-typing of `MutableMapping | MutableSequence` in `util.patch()` triggered dozens of generic structural errors (`Attribute "__closure__" is unknown`, `"object" is not iterable`). Fixing these required either littering the core logic with `# type: ignore` or globally suppressing Pyright's `reportGeneralTypeIssues` rule, which defeats the purpose of the tool.
- **MyPy** was tested as an alternative and proved far more capable of reasoning gracefully about the dynamic abstractions. It correctly identified actual missing imports and edge-case syntax (e.g., missing return types on overridden protocols) without throwing false-positive structural errors on standard Python metaprogramming idioms. MyPy provides the best balance of safety and flexibility for this repository.

## Testing & Orchestration

### Candidates:

1. **Pytest + Tox** (Selected)
1. **Unittest + Nox**
1. **Nose2**

### Evaluation:

- **Pytest** was selected because of its seamless integration with the `hypothesis` library, which is used heavily in `test_hypothesis.py` for property-based fuzz testing of the dynamic collections. It also handles the legacy `unittest.TestCase` classes natively, allowing for a gradual migration.
- **Tox** was selected over Nox simply due to its ubiquitous standard for managing isolated multi-Python-version environments (`py312`, `py313`).
- **Unittest** (standalone) lacks the powerful fixture and parametrization capabilities of Pytest, which are highly beneficial for testing complex, nested closure states.

## Documentation Formatting

### Candidates:

1. **mdformat** (Selected)
1. **markdownlint**
1. **Prettier**

### Evaluation:

- **mdformat** is a highly opinionated Markdown formatter (similar in philosophy to Black or Ruff for Python). It strictly rewrites Markdown to be CommonMark-compliant. This is vastly superior for this project than a simple linter like `markdownlint`, because `mdformat` can automatically fix the files (`mdformat .`) rather than just complaining about them in CI.
- **Prettier** is excellent but requires a Node.js runtime (`npm`/`npx`), whereas `mdformat` is a native Python package that can be easily bundled into the `pyproject.toml` `dev` dependencies alongside Ruff and MyPy.
