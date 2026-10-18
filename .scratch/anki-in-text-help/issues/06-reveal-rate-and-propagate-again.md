# 06 — Reveal, rate, and propagate Again

**What to build:** A pupil can reveal Anki-rendered vocabulary card content in the single card area below the current sentence and rate it from the embedded text workflow, with failed recall reflected across the vocabulary entry's active cards. The view follows Anki's standard card review look and feel while the plugin owns the review flow.

**Blocked by:** 05 — Show review-ahead availability.

**Status:** ready-for-agent

- [ ] Selecting a candidate displays one card at a time in the sentence view's card area, using Anki-rendered question and answer content, the familiar question/reveal/rating sequence, and Anki's scheduler for rating submissions.
- [ ] Scheduling state is re-read before the UI accepts a rating; `Hard`, `Good`, and `Easy` update only the representative card.
- [ ] `Again` updates the representative card first; failure is shown to the pupil and stops further updates.
- [ ] After representative-card success, `Again` is attempted on every non-suspended sibling card; sibling failures are logged and do not interrupt text work.
- [ ] Rating controls reflect availability and suspension state; expected errors are shown in the plugin UI without falsely reporting success.
- [ ] Diagnostics contain technical identifiers and exception details but no vocabulary or source-text content, use a size-limited rotating local log, and can be opened through a registered add-on menu action.
- [ ] Core tests verify rating policy and propagation; collection integration verifies rendered content and scheduler submissions; headless Qt integration loads the add-on, reveals/rates a card, verifies sibling updates and error display, and opens the diagnostic log action.
