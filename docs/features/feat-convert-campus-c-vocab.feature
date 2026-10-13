Feature: Convert Campus C school-book entries

  1. As a user, I want to have Danki CLI to convert a vocabulary of the school book *Campus C* from XHTML or
     flat OpenDocument Text (FODT) input into a CSV file, so that I can import a vocabulary set into Anki. The
     input format is given by tests/test_book_C1.html for the XHTML format and tests/test_book_C2.fodt for the
     flat ODT format.
  2. As a user, I want the Danki CLI to report any potential conversion issue, so that I can be sure whether the
     conversion result is reliable.
  3. As an integrator, I want the output CSV to use the canonical field names from the CONTEXT file and be
     RFC4180-compatible, so downstream importers can consume the file.


  Scenario: Ignore a paragraph starting with "#" silently
    Given the HTML body:
      """
      <p>#testword    meaning 32</p>
      """
    When Danki converts the input
    Then the expected output is empty
    And the console output is:
      """
      Converted 0 entries.
      """


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
      | input                                                                                                                                                                                                                                                           | output                                                                                                                         |
      | <p class="paragraph-P5"><span class="text-T13">ā / ab</span><span class="text-T6"> </span><span class="text-T7">Präp. m. Abl.    </span><span class="text-T8">von, von ... her</span><span class="text-T9">16</span></p>                                        | a / ab,ā / ab (m. Abl.),a / ab (m. Abl.),Präposition,Präp. m. Abl.,"von, von ... her",2,,,,,book1,16,,,,,,,Top500                         |
      | <p class="paragraph-P6"><span class="text-T13">ostendere, ostendō, ostendī</span><span class="text-T11">    zeigen, erklären</span><span class="text-T12">16. 28</span></p>                                                                                     | ostendere,"ostendere, ostendō, ostendī","ostendere, ostendo, ostendi",Verb,,"zeigen, erklären",2,,,,,book1,16;28,,,,,,,Top500        |
      | <p class="paragraph-P5"><span class="text-T10">comes, comitis</span><span class="text-T11">  </span><span class="text-T22">m/f</span><span class="text-T11">    der (die) Begleiter(in), der Gefährte, die Gefährtin</span><span class="text-T12">32</span></p> | comes,"comes, comitis","comes, comitis",Nomen,m/f,"der (die) Begleiter(in), der Gefährte, die Gefährtin",3,,,,,book1,32,,,,,,, |
      | <p class="paragraph-P1"><span class="text-T5">-que</span><span class="text-T6">  angehängt    und</span><span class="text-T8">14</span></p>                                                                                                                     | -que,-que,-que,,angehängt,und,1,,,,,book1,14,,,,,,,                                                                            |
      | <p class="paragraph-P6"><span class="text-T27">tamquam</span><span class="text-T6">   </span><span class="text-T7">Adv.</span><span class="text-T6">    wie</span><span class="text-T8">32</span></p>                                                           | tamquam,tamquam,tamquam,Adverb,Adv.,wie,1,,,,,book1,32,,,,,,,                                                                  |
      | <p class="paragraph-P1"><span class="text-T17">paulō post</span><span class="text-T6">    (ein) wenig später</span><span class="text-T8">26</span></p>                                                                                                          | paulo post,paulō post,paulo post,,,(ein) wenig später,1,,,,,book1,26,,,,,,,                                                    |
      | <p class="paragraph-P6"><span class="text-T13">et ... et</span><span class="text-T6">    sowohl ... als auch</span><span class="text-T8">35</span></p>                                                                                                          | et ... et,et ... et,et ... et,,,sowohl ... als auch,1,,,,,book1,35,,,,,,,Top500                                                |


  Scenario: Convert a complete HTML vocabulary book
    Given the HTML input file "tests/test_book_C1.html"
    When Danki converts the input with book "example_school_book_input"
    Then the output contains 153 vocabulary entries
    And the output contains the canonical CSV field "Headword"
    And at least one output entry has the tag "Top500"


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


  Scenario: Convert a complete FODT vocabulary book
    Given the FODT input file "tests/test_book_C2.fodt"
    When Danki converts the input with book "example_school_book_input"
    Then the output contains 30 vocabulary entries
    And the output contains the canonical CSV field "Headword"
    And at least one output entry has the tag "Top500"


  Scenario: Report a paragraph that is not a vocabulary entry
    Given the HTML body:
      """
      <p><span>testword</span>  not-enough-spaces 32</p>
      """
    When Danki converts the input
    Then the expected output is empty
    And a parsing warning is reported for the paragraph
