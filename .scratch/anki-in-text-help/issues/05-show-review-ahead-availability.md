# 05 — Show review-ahead availability

**What to build:** A pupil can see which vocabulary candidates are currently available for review while working a sentence.

**Blocked by:** 03 — Select surface forms and resolve headwords; 04 — Configure representative cards.

**Status:** ready-for-agent

- [ ] New and learning representative cards are available immediately; review cards become available when at least two thirds of the current interval has elapsed, including overdue cards.
- [ ] `Again` is available without the threshold; successful ratings require review-ahead availability.
- [ ] The sentence UI highlights a surface form when at least one candidate is available and shows availability separately for every ambiguous candidate. On opening a sentence, the card area selects its first rateable form; after each rating it advances through rateable candidates in sentence and candidate order, then wraps to the first candidate that is currently rateable, regardless of previous ratings, including `Again`. It stops only when no candidate remains rateable or the pupil navigates to another sentence; sentence navigation is never gated by card ratings.
- [ ] Suspended representative cards remain viewable but the UI disables rating; buried cards remain reviewable under the normal availability rules.
- [ ] Missing mappings, templates, or generated representative cards produce clear states in the workflow rather than an arbitrary card selection.
- [ ] Core tests cover each card state, the threshold boundary, and sentence-local traversal order, wraparound, repeat presentation after `Again`, and stop behavior when no candidate remains rateable; collection integration verifies the scheduling snapshots; headless Qt integration verifies highlights, per-candidate availability, traversal, and unblocked sentence navigation for new, learning, review, suspended, and buried cards.
