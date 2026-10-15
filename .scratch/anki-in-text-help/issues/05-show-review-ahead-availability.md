# 05 — Show review-ahead availability

**What to build:** A pupil can see which vocabulary candidates are currently available for review while working a sentence.

**Blocked by:** 03 — Select surface forms and resolve headwords; 04 — Configure representative cards.

**Status:** ready-for-agent

- [ ] New and learning representative cards are available immediately; review cards become available when at least two thirds of the current interval has elapsed, including overdue cards.
- [ ] `Again` is available without the threshold; successful ratings require review-ahead availability.
- [ ] The sentence UI highlights a surface form when at least one candidate is available and shows availability separately for every ambiguous candidate.
- [ ] Suspended representative cards remain viewable but the UI disables rating; buried cards remain reviewable under the normal availability rules.
- [ ] Missing mappings, templates, or generated representative cards produce clear states in the workflow rather than an arbitrary card selection.
- [ ] Core tests cover each card state and the threshold boundary; collection integration verifies the scheduling snapshots; headless Qt integration verifies highlights and per-candidate availability for new, learning, review, suspended, and buried cards.
