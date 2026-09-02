Convert Campus C school-book entries
====================================

User Stories
------------

1. As a user, I want to have Danki CLI to convert a vocabulary of the school book *Campus C* from XHTML or
   flat OpenDocument Text (FODT) input into a CSV file, so that I can import a vocabulary set into Anki. The
   input format is given by tests/test_book_C1.html for the XHTML format and tests/test_book_C2.fodt for the
   flat ODT format.
2. As a user, I want the Danki CLI to report any potential conversion issue, so that I can be sure whether the
   conversion result is reliable.
3. As an integrator, I want the output CSV to use the canonical field names from the CONTEXT file and be
   RFC4180-compatible, so downstream importers can consume the file.


Functional acceptance criteria
------------------------------

1. Given an input file with correct vocabulary entries in paragraphs and other text paragraphs mixed in one
   file, when Danki CLI converts this file,it shall detect paragraphs that do not contain vocabulary entries
   and log info for them.

2. Given an input file, when the user converts the HTML file, all CSV entries have the value of the CLI option
   *--book* as `ReferenceBook`. The default value of this CLI option is the stem of the input file name.

3. Given an HTML input file with several entries for the same headword, when the Danki CLI converts this file,
   it shall detect duplicate entries (same headword) and handle them in the following two steps:

    - Compare duplicates with the first entry in all fields and report mismatching fields on the command line
      output.
    - Keep just the first occurrence and drop all later ones,

4. Given an input file, when the Danki CLI converts this file, the resulting CSV schema shall use the field
   names of the CONTEXT file in the specified order and sorted alphabetically according to `Headword`.

5. Given an input file with malformed XML, when the Danki CLI converts this file, Danki reports an error.

6. Given an input file, when a paragraph starts with "#", ignore it silently.


Non-functional acceptance criteria
----------------------------------

None

---

Triage: implemented
