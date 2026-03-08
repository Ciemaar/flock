# Flock

Flock is a library for managing groups of closures in Python, most commonly zero argument lambda closures.
The basic trick is to take a group of lambdas with no parameters and then call them if/when you need their value.
For example:

```python
>>> myList = []
>>> myList.append(lambda:5)
>>> myList.append(lambda:3)
>>> myList.append(lambda:myList[0]()+myList[1]())
>>> [x() for x in myList]
[5, 3, 8]
```

The trick is the last element. As you can see the third lambda includes the list itself.

For Flock this is encapsulated within an implementation of dict called a `FlockDict`.

Flock is mostly useful as a way to memorialize--however temporarily--mathematical models and then allow for execution
or re-execution as you experiment with them non-linearly.

## User Documentation

### Installation

Flock requires Python 3.10 or later.

To install for usage:

```bash
pip install .
```

To install for development (editable mode with dev dependencies):

```bash
pip install -e ".[dev,test]"
```

### Usage Examples

The core object in Flock is the `FlockDict`. It acts like a regular Python dictionary but can seamlessly evaluate callable objects (rules/closures) when their keys are accessed.

#### Basic Usage

You can initialize a `FlockDict` with static data and rules (closures):

```python
from flock import FlockDict

# Define rules
def calc_c(flock):
    return flock['a'] + flock['b']

def calc_d(flock):
    return flock['c'] * 2

# Initialize FlockDict with data and rules
my_flock = FlockDict({
    'a': 10,
    'b': 20,
    'c': calc_c,
    'd': calc_d
})

# Accessing a static value
print(my_flock['a']) # Output: 10

# Accessing a rule evaluates it on the fly
print(my_flock['c']) # Output: 30
print(my_flock['d']) # Output: 60
```

#### Dynamic Updates

When you change underlying data, the rules dynamically re-evaluate using the new data the next time they are accessed:

```python
# Update a dependency
my_flock['a'] = 50

# The dependent rules yield new results
print(my_flock['c']) # Output: 70
print(my_flock['d']) # Output: 140
```

#### Using `patch`

The `flock.util.patch` function allows you to deep-update nested structures within a `FlockDict` or any standard mapping/sequence:

```python
from flock.util import patch

data = {'nested': {'key': 'old_value'}}
patch(data, ['nested', 'key'], 'new_value')
print(data) # Output: {'nested': {'key': 'new_value'}}
```

## Concepts

- **Flock**: a set of related closures, aggregators, and flocks. A flock represents a model or formula of some sort and
  pragmatically will not be changed by exterior components.
- **0 argument closures**: a closure with 0 arguments can be executed at anytime however Python does not guarantee
  that this will not cause an error nor does Flock attempt to do so.
- **Aggregator**: an object that works across a set of closures in one or more flocks applying a common function to them.
  This is like a column in Excel filled entirely with a consistent formula.
- **dataset**: the datavalues in a flock.
- **ruleset**: the rules in a flock - everything in a flock that is not data. Combining data and rules will restore the
  flock, but rules are harder to persist.

## Developer Documentation

This project uses modern Python tooling. It is designed to be easily testable and maintainable.

### Architecture Overview

- **`flock/`**: Contains the core library logic (`FlockDict`, closures, aggregators, utility functions).
- **`mythica/`**: A sample domain implementation demonstrating how Flock can be applied to game mechanics.
- **`test/`**: Unit tests utilizing `pytest` and property-based tests via `hypothesis`.

### Testing

We use `tox` to manage testing environments.

To run tests across all supported Python versions (3.10, 3.11, 3.12), linting, and type checking:

```bash
tox
```

To run just unit tests for a specific version (e.g., Python 3.12):

```bash
tox -e py312
```

To run unit tests directly (requires `pytest` installed):

```bash
pytest
```

### Linting and Formatting

We use `ruff` for linting and formatting.

To run lint checks:

```bash
tox -e lint
```

Or directly:

```bash
ruff check .
ruff format --check .
```

### Type Checking

We use `pyright` for static type checking.

To run type checks:

```bash
tox -e type
```

Or directly:

```bash
pyright .
```

### Continuous Integration (CI)

This project uses GitHub Actions for CI. Workflows are defined in `.github/workflows/tests.yml`.
The CI pipeline automatically runs `tox` across Ubuntu and macOS environments on every push and pull request to ensure that:

1. Tests pass on Python 3.10, 3.11, and 3.12.
1. Code is formatted correctly using `mdformat` and `ruff`.
1. Code is statically type-checked with `pyright`.
1. No structural linting errors exist.

### Contributing Guidelines

- **No Asserts in Production**: Ensure that `assert` statements are not used in `flock/` or `mythica/`. Use explicit exceptions (e.g., `ValueError`, `TypeError`) instead. Asserts are fine for test code.
- **Type Safety**: New functions should include type hints that pass the strict Pyright checks configured in `pyproject.toml`.
- **Formatting**: All commits must pass the formatting checks. Run `tox -e lint` before submitting a pull request to ensure `ruff` and `mdformat` checks pass.
- **Test Coverage**: Strive to write unit tests for any new features or bug fixes. `flock` uses `pytest` and property-based testing heavily.
- **AI Agent Context**: The `AGENTS.md` and `.github/copilot-instructions.md` files provide context and instructions tailored to automated and IDE-based AI assistants working on this repository.

## Supported Python Versions

- Python 3.10
- Python 3.11
- Python 3.12
