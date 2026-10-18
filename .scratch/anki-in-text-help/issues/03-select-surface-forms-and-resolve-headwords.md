# 03 — Select surface forms and resolve headwords

**What to build:** A pupil can select authored help in the current sentence, see supplied notes directly, or choose among possible headwords.

**Blocked by:** 02 — Resume and navigate sentences.

**Status:** ready-for-agent

- [ ] Only described surface forms are interactive in the sentence view; the pupil can select them manually, matching is case-insensitive, and overlapping matches prefer the longest form.
- [ ] Selecting notes-only help displays its notes in the plugin UI without rating controls; selecting an ambiguous form displays every candidate headword in the single card area for the pupil to choose, including candidates whose cards are viewable but currently unrateable.
- [ ] Choosing a candidate resolves its vocabulary entry through the `TextLearning` interface, searching the text unit's deck and then parent decks from nearest to farthest.
- [ ] Headword lookup remains case-sensitive. Duplicate exact matches in a deck and missing vocabulary notes appear as clear user-facing errors in the text workflow.
- [ ] Core tests cover matching, notes, ambiguity, nearest-deck lookup, duplicate matches, and unresolved candidates.
- [ ] Headless Qt integration exercises the rendered sentence, clicks described forms, checks notes-only and ambiguous-candidate views including a viewable but unrateable candidate, chooses a candidate, and verifies user-facing lookup errors.
