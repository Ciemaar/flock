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

## Installation

Flock requires Python 3.10 or later.

To install for usage:

```bash
pip install .
```

To install for development (editable mode with dev dependencies):

```bash
pip install -e ".[dev,test]"
```

## Concepts

* **Flock**: a set of related closures, aggregators, and flocks. A flock represents a model or formula of some sort and
  pragmatically will not be changed by exterior components.
* **0 argument closures**: a closure with 0 arguments can be executed at anytime however Python does not guarantee
  that this will not cause an error nor does Flock attempt to do so.
* **Aggregator**: an object that works across a set of closures in one or more flocks applying a common function to them.
  This is like a column in Excel filled entirely with a consistent formula.
* **dataset**: the datavalues in a flock.
* **ruleset**: the rules in a flock - everything in a flock that is not data. Combining data and rules will restore the
  flock, but rules are harder to persist.

## Development

This project uses modern Python tooling.

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

## Supported Python Versions

* Python 3.10
* Python 3.11
* Python 3.12
