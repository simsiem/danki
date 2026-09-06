Expand fields with auto-generated content
=========================================

User stories
------------

As a user, I want Danki CLI to automatically complement a vocabulary entry with additional information based
on existing field values so that the result needs less manual post-processing. 


Functional acceptance criteria
------------------------------

Danki CLI shall complement the following fields of a vocabulary entry:

`PartOfSpeech`:
    If the field is empty, inspect `NotesForeign`, `FullFormDisplay` and `Meanings` to derive the part of speech.

`FullFormDisplay`:
    If the entry refers to a noun and it follows the regular o- or a- declension, complement the full form
    display by adding the appropriate ending to the stem if missing. Be on the safe side and do not add the
    ending, if the field already contains more than one word (i.e. space in it).


Non-functional acceptance criteria
----------------------------------

None
