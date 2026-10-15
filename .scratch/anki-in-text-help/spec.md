# Anki In-Text Help

Status: ready-for-agent

## Problem Statement

Pupils translating foreign-language texts for school must interrupt their work to look up unfamiliar words and must later repeat much of the same vocabulary in separate Anki review sessions. Existing Anki review is card-oriented and does not connect a word occurrence in a source text to the vocabulary entry the pupil is trying to recall.

Danki needs an Anki Desktop add-on that presents imported texts sentence by sentence, supplies authored help for selectable surface forms, and lets pupils review associated vocabulary without leaving the text workflow. The learning schedule must remain governed by Anki, while one representative card carries the learning progress of an entire vocabulary entry.

## Solution

Add an Anki Desktop workflow called *in-text help*. The pupil first selects an Anki deck and then a text unit stored directly in that deck. The add-on resumes at the pupil's synchronized reading position and presents one sentence at a time.

Only surface forms described by the text unit are selectable. Selecting one either shows supplied notes for material that has no vocabulary entry or lists all possible headwords. Selecting a headword reveals its vocabulary card and permits ratings according to the representative card's Anki scheduling state.

The add-on uses its own text and review view but delegates card rendering and scheduling changes to Anki. Text units, reading positions, and deck configuration synchronize through AnkiWeb using supported collection data. The add-on itself must be installed separately on each Anki Desktop installation.

## User Stories

1. As a pupil, I want to select an Anki deck before selecting a text, so that text work uses the correct subject vocabulary.
2. As a pupil, I want to see the text units stored directly in the selected deck, so that I can choose my assigned text.
3. As a pupil, I want an empty text list when a deck has no text units, so that deck selection remains simple and predictable.
4. As a pupil, I want to import a text-unit JSON file into the selected deck, so that I can add teacher-assigned material.
5. As a pupil, I want re-importing the same text identifier into the same deck to update its note, so that corrected source material does not create duplicates.
6. As a pupil, I want the same text identifier to be usable in another deck, so that different subjects or courses can contain the same text independently.
7. As a pupil, I want imported text units to synchronize through AnkiWeb, so that they are available on my other Anki Desktop installations.
8. As a pupil, I want text work to resume at my last sentence after restarting Anki, so that homework can span several days.
9. As a pupil, I want my reading position to synchronize through AnkiWeb, so that I can continue on another computer.
10. As a pupil, I want re-importing a text unit to preserve my reading position, so that content corrections do not reset my work.
11. As a pupil, I want an updated text with fewer sentences to resume at a valid sentence, so that stale progress cannot break the workflow.
12. As a pupil, I want to navigate to the next and previous sentence, so that I control my progress through the text.
13. As a pupil, I want to restart a text from its first sentence, so that I can work through it again.
14. As a pupil, I want line wrapping in imported material treated as whitespace, so that printed-page formatting does not create false sentences.
15. As a pupil, I want punctuation to determine sentence boundaries, so that the displayed units follow ordinary language structure.
16. As a pupil, I want punctuation and quotation marks preserved in displayed sentences, so that I see the original text faithfully.
17. As a pupil, I want only authored surface forms to be selectable, so that the interface does not promise help it cannot provide.
18. As a pupil, I want surface forms matched without regard to case, so that sentence capitalization does not prevent help.
19. As a pupil, I want a multi-word surface form preferred over overlapping shorter forms, so that phrase-level help is presented as authored.
20. As a text-unit author, I want duplicate surface forms rejected case-insensitively, so that selection behavior is deterministic.
21. As a text-unit author, I want unused surface-form descriptions rejected, so that stale or misspelled entries are detected during import.
22. As a pupil, I want a surface form with supplied notes to show that help directly, so that I can understand material I have not learned as a vocabulary entry.
23. As a pupil, I want supplied notes to remain unrateable, so that unlearned material does not alter my Anki schedule.
24. As a pupil, I want an ambiguous surface form to show every possible headword, so that I must decide which analysis fits the context.
25. As a pupil, I want to select any candidate headword and rate my recognition of it, so that choosing a contextually wrong candidate does not invalidate an honest vocabulary review.
26. As a pupil, I want a clear message when a headword has no matching vocabulary note, so that broken source data is visible.
27. As a pupil, I want a clear message when representative-card configuration is missing or does not identify a generated card, so that the add-on never rates an arbitrary card.
28. As a pupil, I want headword lookup to start in the text unit's deck and walk upward through parent decks, so that nearer subject vocabulary overrides shared parent vocabulary.
29. As a deck maintainer, I want headwords to be unique within an individual deck, so that nearest-deck lookup is deterministic.
30. As a pupil, I want headword matching to remain case-sensitive, so that distinct canonical entries such as `sol` and `Sol` remain separate.
31. As a deck maintainer, I want to configure one representative card template for each vocabulary note type at deck level, so that note-level progress uses the intended test direction.
32. As a deck maintainer, I want representative-card mappings inherited from the nearest configured ancestor deck, so that child decks require configuration only when they differ.
33. As a deck maintainer, I want those mappings synchronized through AnkiWeb, so that learning behavior is consistent across computers.
34. As a pupil, I want the representative card's scheduling state to represent progress for the vocabulary entry, so that progress is managed at note level rather than independently per card.
35. As a pupil, I want new and learning representative cards to be reviewable during text work, so that current learning can continue in context.
36. As a pupil, I want a review card to accept successful ratings after two thirds of its current interval has elapsed, so that text work can perform a useful review shortly before Anki would schedule it.
37. As a pupil, I want `Again` available before that threshold, so that forgetting a word can always be recorded.
38. As a pupil, I want a surface form highlighted when at least one candidate headword has review-ahead availability, so that useful review opportunities are visible in the sentence.
39. As a pupil, I want availability shown separately for each ambiguous candidate, so that one candidate's state does not misrepresent another's.
40. As a pupil, I want a suspended representative card to remain viewable but unrateable, so that text help respects my explicit suspension choice.
41. As a pupil, I want a buried representative card to remain reviewable in text work, so that temporary burial does not block contextual learning.
42. As a pupil, I want to see the card answer before rating it, so that I can judge whether I knew the vocabulary entry.
43. As a pupil, I want `Hard`, `Good`, or `Easy` to advance only the representative card, so that its schedule remains the source of note-level progress.
44. As a pupil, I want `Again` applied first to the representative card, so that the primary progress update is authoritative.
45. As a pupil, I want failure of the representative-card `Again` update reported and further updates stopped, so that the add-on does not claim success without updating note-level progress.
46. As a pupil, I want `Again` attempted on every non-suspended sibling card after the representative card succeeds, so that all active exercises reflect a failed vocabulary test.
47. As a pupil, I want failures on sibling-card updates ignored after being logged, so that a secondary problem does not interrupt text work.
48. As a maintainer, I want diagnostic logging to exclude vocabulary and source-text content, so that logs do not disclose pupils' learning material unnecessarily.
49. As a maintainer, I want a bounded diagnostic log available from the add-on menu, so that failures can be investigated without unbounded local storage.
50. As a pupil, I want the plugin-owned review view to use Anki's rendered card content, so that my card templates remain effective.
51. As a pupil, I want ratings submitted through Anki's scheduler, so that intervals, review history, and FSRS behavior remain correct.
52. As a pupil, I want expected problems displayed as clear messages, so that I can correct imports or deck configuration.
53. As a maintainer, I want the business workflow testable without Anki or Qt, so that most behavior can be verified quickly and deterministically.
54. As a maintainer, I want small integration suites against a real Anki collection and headless Qt, so that adapter assumptions are verified without making the entire suite host-dependent.

## Implementation Decisions

- Target Anki Desktop, using the current stable Anki release as the initial compatibility baseline. AnkiWeb and mobile clients do not run the add-on UI.
- Use hexagonal architecture with one public `TextLearning` interface as the primary driving seam. The UI and level-1 tests call the same interface.
- `TextLearning` provides operations to list and import text units, open and navigate a text, select a surface-form occurrence, reveal candidate help, and submit a rating.
- Expected failures return a pair `(value, error_message)`. Exactly one member is non-null. Unexpected infrastructure failures raise exceptions and are logged.
- Keep the core independent of `anki`, `aqt`, and Qt imports. Enforce this dependency rule automatically.
- Use role-specific outbound ports for text-unit storage, reading-position storage, vocabulary/deck lookup, and card review. A single Anki collection adapter may implement several of these interfaces.
- Use small supporting ports for the current time and diagnostic logging.
- Keep deck-tree lookup, nearest-deck selection, representative-card inheritance, review-ahead calculation, rating propagation, sentence navigation, and matching policy in the core.
- Adapters expose neutral snapshots and collection data; they do not decide business policy.
- Parse JSON in an input codec and map Anki note fields in a storage adapter. Both convert to and from the same `TextUnit` domain object.
- The version-1 JSON object has exactly four top-level fields: `schemaVersion`, `textIdentifier`, `text`, and `vocabularyEntries`.
- `schemaVersion` must equal `1`. The importer rejects unversioned legacy files and unknown schema versions.
- Reject unknown fields instead of silently discarding them, preserving the lossless representation guarantee.
- Each vocabulary description has a `surfaceForm` and exactly one of `headwords` or `notes`.
- `headwords` contains the possible vocabulary entries behind an ambiguous surface form. The student, not the importer, resolves contextual ambiguity.
- `notes` supplies any non-reviewable help for a surface form that has no vocabulary entry, including vocabulary, grammar, names, or other explanations.
- Surface-form matching is Unicode-aware and case-insensitive. Values must be unique under the same normalization.
- Headword lookup is exact and case-sensitive.
- Described surface forms must occur in the text. Text occurrences without descriptions remain valid and non-selectable.
- Prefer the longest description when multi-word and shorter surface forms overlap.
- Normalize line breaks to whitespace before sentence segmentation. Use sentence-ending punctuation as the boundary while retaining punctuation and quotation marks for display.
- Create and maintain one shared text-unit note type for the collection with exactly three fields: `TextIdentifier`, `Text`, and `VocabularyEntries`. `TextIdentifier` is the first/sort field.
- Store `VocabularyEntries` as the JSON array representation. `schemaVersion` is implicit in the managed note type and restored by the version-1 codec.
- A text identifier is unique among text-unit notes stored directly in one Anki deck. Re-import updates that note. The same identifier may exist in another deck.
- Generate one storage card for each text-unit note and keep it suspended. Anki does not provide a durable synchronized cardless-note model.
- Store the synchronized current sentence index as small versioned custom data on the storage card, separate from text-unit content.
- Re-import does not alter reading position. If the stored index exceeds the updated sentence range, clamp it to the final sentence.
- The initial workflow selects a deck and then lists text units stored directly in that deck. Do not pre-scan decks for text units.
- Place the import action and representative-card configuration action on the selected deck's text-list screen.
- Resolve a headword by searching the text unit's exact deck, then each parent deck in order, stopping at the first deck containing a match.
- Multiple exact headword matches within one individual deck are invalid and produce an explicit error.
- Store representative-card mappings as synchronized collection configuration keyed by stable deck and note-type identifiers. Resolve mappings from the nearest configured deck ancestor.
- A representative card is selected by configured card template for the vocabulary note's note type. Missing notes, mappings, templates, or generated cards produce explicit states.
- The Anki adapter translates scheduler state into neutral `New`, `Learning`, or `Review(last_review, due)` snapshots. The core uses an injected clock to calculate elapsed interval fraction.
- New and learning cards have review-ahead availability immediately. Review cards gain it when elapsed time is at least two thirds of the interval from last review to due date. Overdue cards therefore qualify.
- `Again` does not require review-ahead availability. Successful ratings do.
- A suspended representative card is unrateable. A buried representative card is rateable under the normal availability rules.
- Re-read scheduling state immediately before accepting a rating so stale UI state cannot bypass the policy.
- Use a plugin-owned review view. Render question and answer content through Anki and submit answers through its supported scheduler operation; do not calculate or mutate intervals directly.
- On `Hard`, `Good`, or `Easy`, answer only the representative card.
- On `Again`, answer the representative card first. Stop and return an error if that update fails. Then attempt `Again` independently on every non-suspended sibling card, retaining successful updates and ignoring sibling failures.
- Write ignored sibling failures to a size-limited rotating file in the add-on's preserved local data directory. Log technical identifiers and exception details only. Provide an add-on action to open the log.
- Keep the add-on UI thin: it translates `TextLearning` values and errors into Qt views and delegates all workflow decisions to the core.
- Implement both JSON codec directions and guarantee lossless round trips. A user-facing export action is deferred from the initial release.

## Testing Decisions

- The highest and primary test seam is the public `TextLearning` interface. Tests use in-memory adapters and assert externally visible values, errors, stored state, and requested side effects rather than internal helper calls.
- Level-1 tests cover deck and text selection, import create/update behavior, identifier scope, synchronized-position semantics, navigation, index clamping, sentence segmentation, case-insensitive matching, longest-match selection, notes-only help, ambiguous headwords, nearest-deck lookup, same-deck duplicate errors, configuration inheritance, unresolved candidates, availability highlighting, all card states, the two-thirds boundary, suspension and burial, successful ratings, representative-card failure, sibling propagation, and ignored sibling failures.
- Give the JSON codec focused tests for strict version handling, required and unknown fields, mutual exclusivity of `headwords` and `notes`, duplicate normalized surface forms, unused descriptions, case-sensitive headwords, and lossless round trips.
- Give the sentence parser focused multilingual punctuation, quotation, line-break, empty-text, and final-fragment tests.
- Add an architecture test proving core modules do not import Anki, AQT, or Qt.
- Level-2 integration tests remain small and use a real temporary Anki collection on disk. They verify the managed note type, suspended storage cards, field mapping, custom-data position persistence, deck/config synchronization surfaces, nearest-deck queries, rendered card retrieval, and scheduler submissions including multi-card `Again`.
- Level-3 integration tests remain small and run Qt offscreen. They verify add-on loading, menu actions, the deck/text picker, one sentence interaction, card reveal, rating dispatch, and user-facing error display.
- Use `hatch test` for all repository tests. Do not invoke pytest directly.
- Existing tests establish pytest and subprocess-based fixture patterns; the new level-1 tests should remain ordinary package tests and avoid requiring Anki imports.
- Run level-2 tests against pinned `anki` packages compatible with the targeted desktop release. Run level-3 tests separately with matching `aqt`, Qt, and required native Linux libraries.
- Perform one manual smoke test in the official packaged Anki Desktop application before release because headless tests cannot fully prove native dialogs, WebEngine rendering, audio, OS packaging, or interactions with other add-ons.

## Out of Scope

- AnkiWeb, AnkiMobile, or AnkiDroid user interfaces for in-text help.
- Automatic rating of unselected words or completed sentences.
- Sentence completion state or text-pass-based review state.
- Automatic grammatical or contextual disambiguation of candidate headwords.
- Review through Anki's stock Reviewer or temporary filtered decks.
- A separate synchronization backend.
- A user-facing JSON export action in the first release.
- Backward compatibility with the unversioned JSON format using `name`.
- The future multi-round exercise-card and alternating final-test workflow, except for the representative-card semantics and `Again` propagation needed here.
- Reimplementing Anki scheduling, FSRS, card-template rendering, or media handling.
- Guaranteeing compatibility with arbitrary third-party Reviewer hooks inside the plugin-owned review view.

## Further Notes

- The repository examples are migrated to schema version 1 and use `textIdentifier`; the known uppercase `Ab` surface form is corrected to `ab`.
- Text-unit notes, their suspended storage cards, reading positions, and collection configuration synchronize through AnkiWeb. Add-on code and local diagnostic logs do not synchronize.
- The core glossary defines *text unit*, *text identifier*, *sentence*, *representative card*, *review-ahead availability*, and *in-text help*. The discarded *help event* and *auto-review from in-text help* concepts are removed.
- The storage card exists only because Anki requires a card for durable note synchronization. It has no learning role and must not be confused with a vocabulary entry's representative card.
- Start implementation with the core model, ports, in-memory adapters, and level-1 tests. Add the Anki collection adapter next and the minimal Qt shell last.
