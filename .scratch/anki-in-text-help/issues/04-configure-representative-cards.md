# 04 — Configure representative cards

**What to build:** A deck maintainer can choose which card template represents progress for each vocabulary note type, with child decks inheriting the nearest configured mapping.

**Blocked by:** 01 — Import and browse text units; 02 — Resume and navigate sentences.

**Status:** ready-for-agent

- [ ] The selected deck's text-list UI exposes a representative-card configuration action; the pupil can choose a vocabulary note type and one of its card templates for that deck.
- [ ] The UI reads and writes synchronized collection configuration through the `TextLearning`/Anki adapter integration, keyed by stable deck and note-type identifiers.
- [ ] A child deck inherits the nearest configured ancestor's mapping unless it has its own mapping; the UI makes the effective mapping clear and allows a child override.
- [ ] Core tests verify mapping selection and inheritance; collection integration verifies the synchronized configuration surface.
- [ ] Headless Qt integration opens configuration from the selected deck, displays note types/templates, saves a mapping, and verifies it remains available after reopening the view.
