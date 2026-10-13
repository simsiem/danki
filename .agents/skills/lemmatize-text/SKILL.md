---
name: lemmatize-text
description: Lemmatize a Latin textbook text against a vocabulary CSV and write a text JSON under decks/. Use when the user gives a Latin text to analyse or map to headwords.
---

Map every Latin surface form in a text to its possible headwords from a vocabulary CSV and save the result in a JSON file.

## Steps

1. **Gather inputs.** Text name (<name>), full text, and vocabulary CSV (default: `decks/Campus C/CCBuchner Campus C1-2 Wortschatz.csv`). Ask for whichever the user has not given. Done when all three are known.
2. **Preflight the vocabulary.** Load the CSV once and keep its exact `Headword` values as a set. Before composing JSON, derive the checker token set: Use the expression `re.findall(r"[^\W\d_]+\d*", text)` (same as used by `check_vocab.py`), strip digits, use lower case except for proper names, and deduplicate case-insensitively. This is the authoritative entry universe; do not discover missing entries by repeated checker runs.
3. **Tokenize and classify.** For every token in that universe, decide whether it is a Latin form, German framing text, or a proper name. Include every Latin form and every proper name as an entry. Review every token that will otherwise be `uncovered` and confirm it is German before writing.
4. **Lemmatize.** For each Latin form that has a footnote index, take the footnote text as its `notes` field, with no `headwords` field. For each Latin form that is not a footnote word, find all possible inflectional headwords in the CSV, following the rules below. Every non-empty headword list must be a subset of the CSV headword set; never invent a headword or add grammatical annotations not copied from the CSV. Use an empty list when no CSV headword applies. Done when every included form has a complete list for `headwords` or a `notes` field.
5. **Write deterministically.** Write the JSON content to the file specified by the user. Default is a file `<name>.json` in the same directory as the CSV file. Build entries from the deduplicated token universe, strip footnote digits from `surfaceForm`, use lower case except for proper names, and sort entries in code with `sorted(entries, key=lambda e: e["surfaceForm"].lower())`; do not hand-sort a long list. Use the JSON format specified below.
6. **Check once.** Run `python3 .agents/skills/lemmatize-text/check_vocab.py decks/<name>.json "<csv>"`. Before changing anything, interpret its output: `missing headword`, invalid entry fields, `unsorted`, and `duplicate` are construction errors; `uncovered` is acceptable only for the German tokens identified during preflight. Fix the JSON in one pass and rerun once if needed. Done when the run reports `errors: 0` and every uncovered token is accounted for.
7. **Report** the forms with empty lists and the forms with several candidates.

## Lemmatization rules

- Headwords are copied **verbatim** from the CSV, including disambiguators such as `cum (Subj.)`, `in (m. Akk.)`, `iuvenis (Subst.)`, `gaudere (m. Abl.)`.
- List **all** candidate headwords a form can belong to, not just the one the context selects: `in` → `in (m. Akk.)`, `in (m. Abl.)`; `solem` → `sol`, `Sol`; `multa` → `multa`, `multus`.
- The text has no macrons, so forms that differ only in vowel length are ambiguous: `ceciderunt` → `cadere`, `caedere`.
- Split enclitics into both headwords: `causamque` → `causa`, `-que`.
- Footnote words are not translated to a headword. Give them a `notes` field containing the text of the footnote, with no `headwords` field.
- For names missing from the CSV, give them a `notes` field with the German translation of the name, with no `headwords` field.
- Every other form gets a `headwords` field, including an empty list when no CSV headword applies. Never include both `headwords` and `notes` on one entry.

## JSON format

- `name`: the text name.
- `text`: the full text verbatim, German intro/outro and footnote digits (`talem1`) included, lines joined with `\n`.
- `vocabularyEntries`: list of entries with `surfaceForm` and exactly one of `headwords` or `notes`: `{"surfaceForm": ..., "headwords": [...]}` for ordinary forms, or `{"surfaceForm": ..., "notes": ...}` for footnotes and names missing from the CSV.
  - `surfaceForm` has footnote digits stripped, is lowercase except proper names, and is unique.
  - Sorted case-insensitively by `surfaceForm`.
- UTF-8 with literal umlauts, 2-space indent.
