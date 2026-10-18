# 02 — Resume and navigate sentences

**What to build:** A pupil can launch in-text help from Anki Desktop and use the main content area below Anki's top bar to expand a deck, choose one of its text units, then read and navigate the text sentence by sentence. Their position survives restarts and Anki sync.

**Blocked by:** 01 — Import and browse text units.

**Status:** ready-for-agent

- [ ] An Anki Desktop add-on entry point registers the in-text help menu action through supported hooks; the action opens a fresh, collapsed deck list in the main content area while keeping Anki's top bar.
- [ ] Expanding a deck lists text units stored directly in that same view, shows an empty state, and exposes JSON import for the selected deck through `TextLearning` and the collection adapter. Choosing a text switches to the sentence-and-card view; Back returns to the current deck's expanded text list.
- [ ] The sentence-and-card view places the current sentence and its navigation above a single card area. The pupil can move next, previous, or restart regardless of remaining rateable cards, with punctuation and quotation marks preserved after line breaks are normalized for sentence parsing.
- [ ] The current sentence position is stored as synchronized collection data. Re-import preserves it and clamps out-of-range positions to the final sentence.
- [ ] Core tests cover multilingual punctuation, quotations, line breaks, empty text, final fragments, navigation, and clamping; collection integration verifies persistent position data.
- [ ] Headless Qt integration loads the add-on, invokes its menu action, exercises the embedded deck/text picker and import action, opens the sentence-and-card view, navigates a sentence, returns with Back, restarts the workflow, and verifies the resumed position; leaving through Anki's Decks screen and reopening in-text help starts with a fresh deck list.
