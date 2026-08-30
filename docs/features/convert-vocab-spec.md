Problem Statement
=================

Users need a reliable, testable converter that extracts school-book vocabulary from XHTML or FODT input into a CSV matching the project's *vocabulary entry* fields. Ambiguity about parsing rules, duplicate handling, tagging, normalization, and test seams slows implementation and causes inconsistent outputs.


Solution
========

Provide a single, well-typed converter function as the primary seam:

    convert(tree: ElementTree, out_file: TextIO, book: str, console: Console) -> None

This function implements the agreed parsing rules, normalization, duplicate detection, tagging, and CSV export. `cli.py` wires to this function. Tests exercise `convert()` directly by supplying an `ElementTree` and an in-memory `TextIO`.


User Stories
============

1. As a user, I want to have Danki CLI to convert a school-book in XHTML or flat OpenDocument Text (FODT) format into a CSV file, so that I can import a vocabulary set into Anki. The input format is given by tests/test_book_C1.html for the XHTML format and tests/test_book_C2.fodt for the flat ODT format.
2. As a user, I want the Danki CLI to report any potential conversion issue, so that I can be sure whether the conversion result is reliable.
3. As an integrator, I want the output CSV to use the canonical field names from the CONTEXT file and be RFC4180-compatible, so downstream importers can consume the file.


Acceptance criteria
===================

Functional criteria
-------------------

1. Given an input file with correct vocabulary entries in paragraphs and other text paragraphs mixed in one file, when Danki CLI converts this file,it shall detect paragraphs that do not contain vocabulary entries and log info for them.
2. Given an input file, when the user converts the HTML file, all CSV entries have the value of the CLI option *--book* as `ReferenceBook`. The default value of this CLI option is the stem of the input file name.
3. Given an HTML input file with several entries for the same headword, when the Danki CLI converts this file, it shall detect duplicate entries (same headword) and handle them in the following two steps:

    - Compare duplicates with the first entry in all fields and report mismatching fields on the command line output.
    - Keep just the first occurrence and drop all later ones,

4. Given an input file, when the Danki CLI converts this file, the resulting CSV schema shall use the field names of the CONTEXT file in the specified order and sorted alphabetically according to `Headword`.
5. Given an input file with malformed XML, when the Danki CLI converts this file, Danki reports an error.
6. Given an input file, when a paragraph starts with "#", ignore it silently.

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

- Take each HTML of FODT paragraph (``<{namepace}p>``), one-by one.
- Paragraph selection regex: ``r'^[\S].*\s{3,}.*\d+\s*$'`` (Unicode-aware). Non-matches logged with paragraph index + first 20 chars.
- Extract the fields from a matching paragraph with the *field extraction rules* of the next section.
- Duplicate policy: canonical key = normalized `Headword`. Keep first-seen entry; on later occurrences perform exact trimmed equality for all exported fields; on any difference, log mismatch warning with differing fields and both values; do not abort.

Field extraction rules
----------------------

`FullFormDisplay`: 
    This field starts at the beginning of the paragraph. It ends when the following two conditions are fulfilled at the same time:

    1. A *span* element ends and
    2. The last letter of the *span* element or next letter after the *span* is a whitespace separator, but it is not preceded with a "/" or ",". In other words, a pure white space separator terminates `FullFormDisplay`, but ", " and "/ " do not.

    If this field contains three comma-separated elements that are the same except for the prefix "us", "a", "um", then compress it like in the following example:

        beātus, beāta, beātum  ->  beātus, a, um

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

Merging duplicate entries
-------------------------

For two entries of the same headword, some fields can be merged.

`FullFormDisplay`:
    For a comma-separated multi-part entry, choose the value with more parts, if the common parts between both match exactly.
    Example:

        <p><span>audīre, audiō</span>    hören, lernen32</p>
        <p><span>audīre, audiō, audīvī, audītum</span>    hören, lernen32</p>
    
    Results in

        'audire,"audīre, audiō, audīvī, audītum","audire, audio, audivi, auditum",,,"hören, lernen",2,,,,,book1,32,,,,,,,',

`NotesForeign`:
    If this field is empty in one entry but not in the other one, choose the non-empty value.

`Meanings`:
    This field must match exactly in both entries. No further merging rules.

`ReferenceSection`:
    Consider the referenced sections as a set of integers. Take the larger set if the smaller set is a subset.
    Otherwise report a mismatch.

`Tags`:
    If this field is empty in one entry but not in the other one, choose the non-empty value.

`FullFormNormalized` and `PartOfSpeech` are derived from the above merged values as described in the previous
section.


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
