Feature: Convert Campus C school-book entries
  As a user
  I want Danki CLI to convert Campus C vocabulary from XHTML or FODT into CSV
  So that I can import the vocabulary set into Anki

  The converter accepts vocabulary entries mixed with other text paragraphs,
  reports potential conversion issues, and writes RFC 4180-compatible CSV
  using the canonical field names.

  # Source: tests/test_converter.py::test_single_paragraph_variants
  Scenario Outline: Convert HTML paragraphs into CSV rows
    Given the HTML body:
      """
      <input>
      """
    When Danki converts it with book "book1"
    Then it outputs the CSV body:
      """
      <output>
      """
    And the output uses the canonical CSV fields
    And no mismatch warning is reported

    Examples:
      | input                                                                                  | output                                                                                                      |
      | <p><span>auxilium</span>    die Hilfe15</p>                                            | auxilium,"auxilium, auxiliī","auxilium, auxilii",Nomen,,die Hilfe,1,,,,,book1,15,,,,,,, |
      | <p><span>ā / ab</span> Präp. m. Abl.    von, von ... her16</p>                         | a / ab,ā / ab (m. Abl.),a / ab (m. Abl.),Präposition,Präp. m. Abl.,"von, von ... her",2,,,,,book1,16,,,,,,, |
      | <p><span>ostendere, ostendō, ostendī</span>    zeigen, erklären<span>16. 28</span></p> | ostendere,"ostendere, ostendō, ostendī","ostendere, ostendo, ostendi",Verb,,"zeigen, erklären",2,,,,,book1,16;28,,,,,,, |

  # Source: tests/test_integration_example.py::test_integration_convert_example
  Scenario: Convert a complete HTML vocabulary book
    Given the HTML input file "tests/test_book_C1.html"
    When Danki converts the input with book "example_school_book_input"
    Then the output contains 153 vocabulary entries
    And the output contains the canonical CSV field "Headword"
    And at least one output entry has the tag "Top500"

  # Source: tests/test_converter.py::test_single_paragraph_variants
  Scenario Outline: Convert FODT paragraphs into CSV rows
    Given the FODT body:
      """
      <input>
      """
    When Danki converts the input with book "book1"
    Then it outputs the CSV body:
      """
      <output>
      """
    And the output uses the canonical CSV fields
    And no mismatch warning is reported

    Examples:
      | input                                                                                                                                                                                                                                                                                                                                                                                                | output                                                                                                                     |
      | <text:p text:style-name="P25" loext:marker-style-name="T16"><text:span text:style-name="T17">Alexander, Alexandrī</text:span><text:span text:style-name="T19"> <text:s text:c="2"/></text:span><text:span text:style-name="T20"><text:s/>Alexander der Große </text:span><text:span text:style-name="T21">(König von Makedonien)</text:span><text:span text:style-name="T22">38</text:span></text:p> | Alexander,"Alexander, Alexandrī","Alexander, Alexandri",,,Alexander der Große (König von Makedonien),1,,,,,book1,38,,,,,,, |
      | <text:p text:style-name="P25" loext:marker-style-name="T24"><text:span text:style-name="T11">bene</text:span><text:span text:style-name="T20"> </text:span><text:span text:style-name="T21">Adv. <text:s text:c="3"/></text:span><text:span text:style-name="T20">gut</text:span><text:span text:style-name="T22">4</text:span></text:p>                                                             | bene,bene,bene,Adverb,Adv.,gut,1,,,,,book1,4,,,,,,,Top500                                                                  |

  # Source: tests/test_integration_example.py::test_integration_convert_example
  Scenario: Convert a complete FODT vocabulary book
    Given the FODT input file "tests/test_book_C2.fodt"
    When Danki converts the input with book "example_school_book_input"
    Then the output contains 30 vocabulary entries
    And the output contains the canonical CSV field "Headword"
    And at least one output entry has the tag "Top500"

  # Source: tests/test_converter.py::test_non_matching_paragraph_logged
  Scenario: Report a paragraph that is not a vocabulary entry
    Given the HTML body:
      """
      <p><span>testword</span>  not-enough-spaces 32</p>
      """
    When Danki converts the input
    Then the expected output is empty
    And a parsing warning is reported for the paragraph

  # Source: tests/test_converter.py::test_single_csv_passthrough_matches_reference
  Scenario: Pass through Danki CSV input
    Given the CSV input:
      """
      Headword,FullFormDisplay,FullFormNormalized,PartOfSpeech,NotesForeign,Meanings,NumberOfMeanings,NotesNative,MnemonicHint,PronunciationText,AudioUrl,ReferenceBook,ReferenceSection,Exercise1Front,Exercise1Back,Exercise2Front,Exercise2Back,Exercise3Front,Exercise3Back,Tags
      -ne,-ne,-ne,,,Partikel im dir. Fragesatz (unübersetzt),1,,,,,Campus C1,13,,,,,,,Top500
      a / ab,ā / ab (m. Abl.),a / ab (m. Abl.),Präposition,Präp. m. Abl.,"von, von ... her",2,,,,,Campus C1,16,,,,,,,Top500
      abire,"abīre, abeō, abiī","abire, abeo, abii",Verb,B,weggehen,1,C,D,E,F,Campus C1,37,G,H,I,J,K,L,Top500
      Aeneas,"Aenēās, Aenēae","Aeneas, Aeneae",Nomen,m,Äneas (Trojaner und Stammvater der Römer),1,,,,,Campus C1,30,,,,,,,
      Romulus / Remus,Rōmulus / Remus,Romulus / Remus,Nomen,,Romulus / Remus,1,Zwillingsbrüder und sagenhafte Gründer Roms,,,,Campus C1,32,,,,,,,
      Tarquinius Superbus,Tarquinius Superbus,Tarquinius Superbus,Nomen,,Tarquinius Superbus,1,Letzter etruskischer König von Rom,,,,Campus C1,36,,,,,,,
      vox,"vōx, vōcis","vox, vocis",Nomen,f,"die Stimme, die Äußerung, der Laut",3,,,,,Campus C1,25,,,,,,,Top500
      """
    When Danki converts the input with book "Campus C1"
    Then the output CSV is identical to the input CSV
