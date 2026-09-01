Title: Treat `_FIELDNAMES` as the canonical CSV schema
Date: 2026-09-01
Status: accepted

Context
-------
The `src/danki/converter.py` module defines a top-level `_FIELDNAMES` list which determines the CSV header order produced by `convert()`. Tests and downstream consumers rely on this ordering and the presence of these fields.

Decision
--------
We will treat the `_FIELDNAMES` list in `src/danki/converter.py` as the canonical, immutable CSV schema for the `danki convert` command unless an explicit ADR is created to change it. For the Merge Files feature, adapters and the updated `convert()` must map inputs into this schema and must not alter the header ordering or field set.

Consequences
------------
- Backwards compatibility: Consumers and tests remain stable because the CSV header and column ordering are preserved.
- Migration cost: Any future change to the CSV schema will require an explicit ADR, tests updates, and a deliberate migration plan for consumers.
- Implementation constraint: Input adapters must normalize and drop or ignore extra fields; provenance or additional metadata will not be added to output CSV.

Rationale
---------
Changing a CSV header is a breaking change for downstream users and test fixtures. The Merge Files feature's goals emphasize determinism and preserving existing console messages and output ordering; treating `_FIELDNAMES` as canonical enforces that.

Migration / Reversal
--------------------
To change the CSV schema in the future, create a new ADR that documents the motivation, compatibility plan, and how to update tests and downstream consumers. Include a deprecation period and tooling to transform old CSVs to the new schema.

Authors
-------
- Walter (author)
