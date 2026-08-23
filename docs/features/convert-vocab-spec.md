Problem Statement
=================

Users need a reliable, testable converter that extracts school-book vocabulary from XHTML input into a CSV matching the project's *vocabulary entry* fields. Ambiguity about parsing rules, duplicate handling, tagging, normalization, and test seams slows implementation and causes inconsistent outputs.


Solution
========

Provide a single, well-typed converter function as the primary seam:

    convert(tree: ElementTree, out_file: TextIO, book: str, console: Console) -> None

This function implements the agreed parsing rules, normalization, duplicate detection, tagging, and CSV export. `cli.py` wires to this function. Tests exercise `convert()` directly by supplying an `ElementTree` and an in-memory `TextIO`.


User Stories
============

1. As a user, I want to have Danki CLI to convert a school-book XHTML into a CSV, so that I can import vocabulary into Anki. The input format is given by docs/example_school_book_input.html.
2. As a user, I want the Danki CLI to report any potential conversion issue, so that I can be sure whether the conversion result is reliable.
3. As an integrator, I want the output CSV to use the canonical field names from the CONTEXT file and be RFC4180-compatible, so downstream importers can consume the file.


Acceptance criteria
===================

Functional criteria
-------------------

1. Given an HTML input file with correct vocabulary entries in paragraphs and other text paragraphs mixed in one file, when Danki CLI converts this file,it shall detect paragraphs that do not contain vocabulary entries and log info for them.
2. Given an HTML input file called example.html, when the user converts the HTML file, all CSV entries have the value of the CLI option *--book* as `ReferenceBook`. The default value of this CLI option is the stem of the HTML file name.
3. Given an HTML input file with several entries for the same headword, when the Danki CLI converts this file, it shall detect duplicate entries (same headword) and handle them in the following two steps:

    - Compare duplicates with the first entry in all fields and report mismatching fields on the command line output.
    - Keep just the first occurrence and drop all later ones,

4. Given an HTML input file, when the Danki CLI converts this file, the resulting CSV schema shall use the field names of the CONTEXT file in the specified order.
5. Given an HTML input file with malformed XML, when the Danki CLI converts this file, Danki reports an error.
6. Given an HTML input file, when a paragraph starts with "#", ignore it silently.

Non-functional criteria
-----------------------

1. Danki shall follow hexagonal architecture principles with injectable objects to the business logic so it is easier to maintain and to extend in the future.


Implementation Decisions
========================

Component design decisions
--------------------------

- Error handling: `converter.py` reports errors as exceptions. The module `cli.py` prints them and results in exit code `1`.

File parsing rules
------------------

- Take each HTML paragraph (``<p>``), one-by one.
- Paragraph selection regex: ``r'^[\S].*\s{3,}.*\d+\s*$'`` (Unicode-aware). Non-matches logged with paragraph index + first 20 chars.
- Extract the fields from a matching paragraph with the *field extraction rules* of the next section.
- Duplicate policy: canonical key = normalized `Headword`. Keep first-seen entry; on later occurrences perform exact trimmed equality for all exported fields; on any difference, log mismatch warning with differing fields and both values; do not abort.

Field extraction rules
----------------------

`FullFormDisplay`: 
    Two options
    
    - Text from paragraph start up to the first 2+ spaces.
    - Content of first HTML *span* element.

`FullFormNormalized`:
    NFKD → strip combining marks → collapse whitespace.

`Headword`:
    first word of `FullFormNormalized` (stops at first whitespace or `,`), but allow " / " inside.

`NotesForeign`:
    The substring between first `FullFormDisplay` and `Meanings` is a note.

`PartOfSpeech`:
    If `NotesForeign` contains one of the following strings, fill `PartOfSpeech` with the associated word from the following list.

    * "Adv." -> Adverb
    * "Präp." -> Präposition
    * "Subj." -> Subjunktion
    * "^[mfn]$", "[mfn] ", "m/f" -> Nomen

`Meanings`:
    substring between the last run of 3+ spaces and next numeric token; store as-is.

`ReferenceSection`:
    trailing numeric tokens stored as `;`-separated list.

`Tags`:
    *Top500* when color #0070c0 present in stylesheet or inline styles or ``<font color>``.


Testing Decisions
=================

- Module tests of `converter.py` shall run without console and filesystem access. They shall mock both..
- Use `docs/example_school_book_input.html` as a golden integration sample and smaller crafted XHTML strings for module tests.


Out of Scope
============

- Robust HTML parsing for totally malformed HTML beyond ElementTree fallback.  
- Merge heuristics for conflicting duplicates (keep first only).  
- New domain fields not in `CONTEXT.rst`.

---

Triage: implemented
