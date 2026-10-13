Feature: Expand fields with auto-generated content
  As a user
  I want Danki CLI to automatically complement a vocabulary entry with additional information
  based on existing field values
  So that the result needs less manual post-processing

  It complements and fixes `FullFormDisplay` and `PartOfSpeech`.


  Scenario Outline: Expand entries depending on the part of speech
    Given the HTML body:
      """
      <input>
      """
    When Danki converts it with book "book1"
    Then it outputs the CSV body:
      """
      <output>
      """

    # Conjunctions: Transform `NotesForeign` to `PartOfSpeech`
    Examples:
      | input                                                                     | output                                                                                                                  |
      | <p><span>dum</span>  Subj.    während, solange, bis19</p>                 | dum,dum,dum,Subjunktion,Subj.,"während, solange, bis",3,,,,,book1,19,,,,,,,                                             |
  
    # Adjectives: Compress subforms in `FullFormDisplay` and fill `PartOfSpeech`.
    Examples:
      | input                                                                     | output                                                                                                                  |
      | <p><span>beātus, beāta, beātum</span>    glücklich, reich36</p>           | beatus,"beātus, a, um","beatus, a, um",Adjektiv,,"glücklich, reich",2,,,,,book1,36,,,,,,,                               |

    # Adverbs: Fill `PartOfSpeech`
    Examples:
      | input                                                                     | output                                                                                                                  |
      | <p><span>tamquam</span> Adv.    wie32</p>                                 | tamquam,tamquam,tamquam,Adverb,Adv.,wie,1,,,,,book1,32,,,,,,,                                                           |

    # Nouns: Fill `PartOfSpeech` by inspection of `NotesForeign` and `Meanings` and add subforms in `FullFormDisplay`.
    # Do not change `FullFormDisplay` if it is a phrase instead of a single noun.
    Examples:
      | input                                                                     | output                                                                                                                  |
      | <p><span>amīca</span>    die Freundin15</p>                               | amica,"amīca, amīcae","amica, amicae",Nomen,,die Freundin,1,,,,,book1,15,,,,,,,                                         |
      | <p><span>amīcus</span>    der Freund15</p>                                | amicus,"amīcus, amīcī","amicus, amici",Nomen,,der Freund,1,,,,,book1,15,,,,,,,                                          |
      | <p><span>auxilium</span>    die Hilfe15</p>                               | auxilium,"auxilium, auxiliī","auxilium, auxilii",Nomen,,die Hilfe,1,,,,,book1,15,,,,,,,                                 |
      | <p><span>iuvenis, iuvenis</span> m    der junge Mann32</p>                | iuvenis,"iuvenis, iuvenis","iuvenis, iuvenis",Nomen,m,der junge Mann,1,,,,,book1,32,,,,,,,                              |
      | <p><span>līberī, līberōrum</span> m Pl.    die Kinder26</p>               | liberi,"līberī, līberōrum","liberi, liberorum",Nomen,m Plural,die Kinder,1,,,,,book1,26,,,,,,,                          |
      | <p><span>res publica</span>    der Staat41</p>                            | res publica,res publica,res publica,,,der Staat,1,,,,,book1,41,,,,,,,                                                   |

    # Prepositions: Fill `PartOfSpeech` by inspection of `NotesForeign` and add case info to `FullFormDisplay`.
    Examples:
      | input                                                                     | output                                                                                                                  |
      | <p><span>ā / ab</span> Präp. m. Abl.    von, von ... her16</p>            | a / ab,ā / ab (m. Abl.),a / ab (m. Abl.),Präposition,Präp. m. Abl.,"von, von ... her",2,,,,,book1,16,,,,,,,           |

    # Prepositions: Fill `PartOfSpeech` by inspection of `FullFormDisplay`
    Examples:
      | input                                                                     | output                                                                                                                  |
      | <p><span>ostendere, ostendō, ostendī</span>    zeigen, erklären16. 28</p> | ostendere,"ostendere, ostendō, ostendī","ostendere, ostendo, ostendi",Verb,,"zeigen, erklären",2,,,,,book1,16;28,,,,,,, |


  Scenario Outline: Remove outer parenthesis from NotesForeign but not inner parenthesis
    Given the HTML body:
      """
      <input>
      """
    When Danki converts it with book "book1"
    Then it outputs the CSV body:
      """
      <output>
      """
    Examples:
      | input                                                                     | output                                                                                                                  |
      | <p><span>-que</span>  (angehängt)    und14</p>                                                                                                                                                                                                 | -que,-que,-que,,angehängt,und,1,,,,,book1,14,,,,,,, |
      | <p class="paragraph-P6"><span class="text-T21">urbs, urbis</span><span class="text-T11">  </span><span class="text-T22">f</span><span class="text-T11"> (Gen. Pl. -ium)    die Stadt; die Stadt Rom</span><span class="text-T12">22</span></p> | urbs,"urbs, urbis","urbs, urbis",Nomen,f (Genitiv Plural -ium),die Stadt; die Stadt Rom,2,,,,,book1,22,,,,,,, |
