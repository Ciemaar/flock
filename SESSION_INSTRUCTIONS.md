# Session Instructions

## Initial Request
* Adapt `index_reference` and `attr_reference` to use the `glom` library.
* Build this work on top of the branch `modernize-codebase-pyproject-15401310875321764212`.

## Clarifications Given During Planning
1. **Adopting glom Standards**: Adopt `glom` standards since the only use of these functions is within this codebase as an example.
2. **Error Handling & Defaults**: The change in errors (using `glom`'s specific exceptions instead of `KeyError` or `AttributeError`) is acceptable.
3. **Dependencies**: `glom` should become a new dependency.

## New Instructions
* Create a document describing all the instructions given in this session.
