# 01 — Import and browse text units

**What to build:** A pupil can choose a deck, see the text units stored directly in it (including an empty list), and import a text unit into that deck.

**Blocked by:** None — can start immediately.

**Status:** resolved

- [x] Import accepts only the version-1 JSON contract, rejects unknown or invalid fields, and round-trips text units without information loss.
- [x] Surface-form descriptions are validated for case-insensitive normalized duplicates and unused descriptions.
- [x] Import creates or updates a text unit scoped to the selected deck; the same identifier can exist in another deck.
- [x] Text units use the managed synchronized note representation and a suspended storage card; re-import updates content without creating duplicates.
- [x] Core tests run without Anki or Qt, and collection integration verifies the managed note, field mapping, and storage card.
