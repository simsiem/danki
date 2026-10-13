# Feature files

How the engineering skills should consume this repo's BDD feature files.

The black-box behaviour spec, in Gherkin, executable. They answer "what does the software do, observable from outside along the seam of the module". They are permanent and are the sole source of truth for behaviour.

Two groups of behaviour specs and test cases:

1. Business logic: `tests/test_<area>_features.py` loads every file in `docs/features/<area>/` via _pytest-bdd_, so these run as part of `hatch test`. They are fast and lean without real AQT/Qt dependencies.

2. Anki Desktop integration: `tests_ankiint/test_<area>_features.py` loads every file in `docs/features/<area>_ankiint/`. `hatch run ankiint:test` executes them. Run that command when changing the installed add-on or its Qt workflow. Their real AQT/Qt dependencies stay outside ordinary `hatch test` runs.

Naming convention: `docs/features/<area>/feat-<slug>.feature`.

Area: Functional area with its own module for the business logic, like

- converter: for the vocabulary conversion functionality of the Danki CLI
- textlearning: for the Anki plugin that supports the student on learning with text units
