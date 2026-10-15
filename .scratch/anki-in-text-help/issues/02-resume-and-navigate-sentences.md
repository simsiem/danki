# 02 — Resume and navigate sentences

**What to build:** A pupil can launch in-text help from Anki Desktop, choose a deck and one of its text units, then read and navigate the text sentence by sentence. Their position survives restarts and Anki sync.

**Blocked by:** 01 — Import and browse text units.

**Status:** ready-for-agent

- [ ] An Anki Desktop add-on entry point registers the in-text help menu action through supported hooks, and the action opens the plugin-owned workflow.
- [ ] The UI lets the pupil select a deck, lists text units stored directly in that deck, shows an empty state, and imports a JSON file into the selected deck through `TextLearning` and the collection adapter.
- [ ] Opening a text unit displays its current sentence; the pupil can move next, previous, or restart, with punctuation and quotation marks preserved after line breaks are normalized for sentence parsing.
- [ ] The current sentence position is stored as synchronized collection data. Re-import preserves it and clamps out-of-range positions to the final sentence.
- [ ] Core tests cover multilingual punctuation, quotations, line breaks, empty text, final fragments, navigation, and clamping; collection integration verifies persistent position data.
- [ ] Headless Qt integration loads the add-on, invokes its menu action, exercises the deck/text picker and import action, navigates a sentence, restarts the workflow, and verifies the resumed position.
