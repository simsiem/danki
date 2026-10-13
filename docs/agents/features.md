# Feature files

How the engineering skills should consume this repo's BDD feature files.

The black-box behaviour spec, in Gherkin. Executable —
`tests/test_<area>_features.py` loads every file in `docs/features/<area>/` via `pytest-bdd`'s `scenarios()`, so
these run as part of `hatch test`. They answer "what does the software do, observable from outside along the seam of the module".

They are permanent and are the sole source of truth for behaviour.

Naming convention: `docs/features/<area>/feat-<slug>.feature`.

Area: Functional area with its own module for the business logic, like

- converter: for the vocabulary conversion functionality of the Danki CLI
- textlearning: for the Anki plugin that supports the student on learning with text units
