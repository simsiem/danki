Feature: Merge several input files into one Anki deck
  As a user
  I want Danki CLI to process several input files into the same vocabulary list
  So that I can merge files published for the same book series, or iterate on the
  input data and the resulting CSV file in cycles

  Merging follows the rules in docs/design/dsgn-vocabulary-entry-merging.rst.


  Scenario: Merge a CSV file with vocabulary files of two other formats
    Given the CSV input:
      """
      Headword,FullFormDisplay,FullFormNormalized,PartOfSpeech,NotesForeign,Meanings,NumberOfMeanings,NotesNative,MnemonicHint,PronunciationText,AudioUrl,ReferenceBook,ReferenceSection,Exercise1Front,Exercise1Back,Exercise2Front,Exercise2Back,Exercise3Front,Exercise3Back,Tags
      a / ab,ā / ab (m. Abl.),a / ab (m. Abl.),Präposition,Präp. m. Abl.,"von, von ... her",2,,,,,Campus C1,16,,Ex1B,,,,,Top500
      accipere,"accipere","accipere",Verb,,"erhalten, erfahren, annehmen",3,,,,,Campus C1,34,,,,,,,Top500
      """
    And the FODT body:
      """
      <text:p><text:span>abire</text:span>    weggehen37</text:p>
      """
    And the HTML body:
      """
      <p><span>accipere, accipiō, accēpī, acceptum</span>    erhalten, erfahren, annehmen34</p>
      """
    When Danki converts the CSV input, then the FODT input, then the HTML input with book "Campus C1"
    Then it outputs the CSV body:
      """
      a / ab,ā / ab (m. Abl.),a / ab (m. Abl.),Präposition,Präp. m. Abl.,"von, von ... her",2,,,,,Campus C1,16,,Ex1B,,,,,Top500
      abire,abire,abire,,,weggehen,1,,,,,Campus C1,37,,,,,,,
      accipere,"accipere, accipiō, accēpī, acceptum","accipere, accipio, accepi, acceptum",Verb,,"erhalten, erfahren, annehmen",3,,,,,Campus C1,34,,,,,,,Top500
      """

  Scenario: Report mismatch and keep first occurance for duplicate entries with deviating meanings
    Given the HTML body:
      """
      <p><span>ācer</span>   energisch 32</p>
      <p><span>et</span>    und 5</p>
      <p><span>ācer</span>   anders 32</p>
      """
    When Danki converts it with book "book1"
    Then it outputs the CSV body:
      """
      acer,ācer,acer,,,energisch,1,,,,,book1,32,,,,,,,
      et,et,et,,,und,1,,,,,book1,5,,,,,,,
      """
    And a mismatch warning is reported


  Scenario: Report mismatch and keep first occurance for duplicate entries with deviating ReferenceSection
    Given the HTML body:
      """
      <p><span>ācer</span>   energisch 32</p>
      <p><span>et</span>    und 5</p>
      <p><span>ācer</span>   energisch 3</p>
      """
    When Danki converts it with book "book1"
    Then it outputs the CSV body:
      """
      acer,ācer,acer,,,energisch,1,,,,,book1,32,,,,,,,
      et,et,et,,,und,1,,,,,book1,5,,,,,,,
      """
    And a mismatch warning is reported


  Scenario: Report mismatch and keep first occurance for duplicate entries with deviating joint grammatical subform
    Given the HTML body:
      """
      <p><span>audīre, audiō</span>    hören, lernen32</p>
      <p><span>audīre, audio, audīvī, audītum</span>    hören, lernen32</p>
      """
    When Danki converts it with book "book1"
    Then it outputs the CSV body:
      """
      audire,"audīre, audiō","audire, audio",Verb,,"hören, lernen",2,,,,,book1,32,,,,,,,
      """
    And a mismatch warning is reported


  Scenario: Report mismatch and keep first occurance of Meanings, while merging expanded FullFormDisplay from second occurance.
    Given the HTML body:
      """
      <p><span>audīre, audiō</span>    hören, lernen32</p>
      <p><span>audīre, audiō, audīvī, audītum</span>    hören32</p>
      """
    When Danki converts it with book "book1"
    Then it outputs the CSV body:
      """
      audire,"audīre, audiō, audīvī, audītum","audire, audio, audivi, auditum",Verb,,"hören, lernen",2,,,,,book1,32,,,,,,,
      """
    And a mismatch warning is reported


  Scenario Outline: Merge compatible duplicate entries without a mismatch warning
    Given the HTML body:
      """
      <input>
      """
    When Danki converts it with book "book1" showing merge messages
    Then it outputs the CSV body:
      """
      <output>
      """
    And no mismatch warning is reported
    And a merge is reported

    Examples:
      | input                                                                                                                     | output                                                                                                                           |
      | <p><span>audīre, audiō</span>    hören, lernen32</p><p><span>audīre, audiō, audīvī, audītum</span>    hören, lernen32</p> | audire,"audīre, audiō, audīvī, audītum","audire, audio, audivi, auditum",Verb,,"hören, lernen",2,,,,,book1,32,,,,,,,           |
      | <p><span>Rōma, Rōmae</span>    die Stadt Rom32</p><p><span>Rōma</span>    die Stadt Rom32</p>                             | Roma,"Rōma, Rōmae","Roma, Romae",Nomen,,die Stadt Rom,1,,,,,book1,32,,,,,,,                                                      |
      | <p><span>Rōma, Rōmae</span>    die Stadt Rom32</p><p><span>Rōma, Rōmae</span>    die Stadt Rom32.21</p>                   | Roma,"Rōma, Rōmae","Roma, Romae",Nomen,,die Stadt Rom,1,,,,,book1,21;32,,,,,,,                                                   |

  Scenario: Report mismatches and merges across separate input files with a converted-entries summary
    Given the HTML input file "first.html" with body:
      """
      <p><span>ācer</span>   energisch 32</p>
      """
    And the HTML input file "second.html" with body:
      """
      <p><span>ācer</span>   anders 32</p>
      <p><span>ācer</span>   anders 32,50</p>
      """
    When Danki converts "first.html", then "second.html" with book "book1" showing merge messages
    Then the console output is:
      """
      second.html: acer: Merge ReferenceSection - previous = "32", chosen = "32;50".
      second.html: acer: Mismatch for Meanings - previous = "energisch", later = "anders".
      Converted 1 entries.
      """

  Scenario: Report mismatches but no merges across separate input files with a converted-entries summary
    Given the HTML input file "first.html" with body:
      """
      <p><span>ācer</span>   energisch 32</p>
      """
    And the HTML input file "second.html" with body:
      """
      <p><span>ācer</span>   anders 32</p>
      <p><span>ācer</span>   anders 32,50</p>
      """
    When Danki converts "first.html", then "second.html" with book "book1" showing no merge messages
    Then the console output is:
      """
      second.html: acer: Mismatch for Meanings - previous = "energisch", later = "anders".
      Converted 1 entries.
      """
