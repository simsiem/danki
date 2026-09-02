Parsing of Campus C vocabulary files
====================================

File parsing rules
------------------

- The input file can be in XHTML or FODT format. Both are related. Use *etree* for XML parsing.
- Take each HTML or FODT paragraph (``<{namepace}p>``), one-by one.
- Paragraph selection regex: ``r'^[\S].*\s{3,}.*\d+\s*$'`` (Unicode-aware). Non-matches logged with paragraph
  index + first 20 chars.
- Extract the fields from a matching paragraph with the *field extraction rules* of the next section.
- Duplicate policy: canonical key = normalized `Headword`. Keep first-seen entry; on later occurrences perform
  exact trimmed equality for all exported fields; on any difference, log mismatch warning with differing
  fields and both values; do not abort.


Field extraction rules
----------------------

The following fields are part those directly written in the input file. Other fields are derived from them as
specified in the next section.

`FullFormDisplay`: 
    This field starts at the beginning of the paragraph. It ends when the following two conditions are
    fulfilled at the same time:

    1. A *span* element ends and
    2. The last letter of the *span* element or next letter after the *span* is a whitespace separator, but it
       is not preceded with a "/" or ",". In other words, a pure white space separator terminates
       `FullFormDisplay`, but ", " and "/ " do not.

    If this field contains three comma-separated elements that are the same except for the prefix "us", "a",
    "um", then compress it like in the following example:

        beātus, beāta, beātum  ->  beātus, a, um

`NotesForeign`:
    The substring between first `FullFormDisplay` and `Meanings` is a note.

`Meanings`:
    substring between the last run of 3+ spaces and next numeric token; store as-is.

`ReferenceSection`:
    trailing numeric tokens stored as `;`-separated list.

`Tags`:
    *Top500* when color #0070c0 present in stylesheet or inline styles or ``<font color>``.


Derived fields
--------------

`Headword`:
    first word of `FullFormNormalized` (stops at first whitespace or `,`), but allow " / " inside.

`FullFormNormalized`:
    NFKD → strip combining marks → collapse whitespace.

`PartOfSpeech`:
    If `NotesForeign` contains one of the following strings, fill `PartOfSpeech` with the associated word from
    the following list.

    * "Adv." -> Adverb
    * "Präp." -> Präposition
    * "Subj." -> Subjunktion
    * "^[mfn]$", "[mfn] ", "m/f" -> Nomen

`NumberOfMeanings`
    The field `Meanings` contains several native language translations for the vocabulary entry. The are
    separated with "," or ";". Count the parts in `Meanings` and fill the count here.

`ReferenceBook`
    Either given by the user directly as input parameter or derived from the input file stem.


Out of Scope
------------

- Robust HTML parsing for malformed HTML beyond ElementTree fallback.  


Testing Decisions
-----------------

- Module tests use small crafted strings (XHTML, FODT and CSV snippets).
- Use `docs/test_book_C1.html` as a golden integration sample for XHMTL and `docs/test_book_C2.fodt` for FODT.

