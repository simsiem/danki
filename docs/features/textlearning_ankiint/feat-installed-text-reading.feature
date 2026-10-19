Feature: Read text units through the installed Anki Desktop add-on

  Scenario: Closing and reopening a text resumes the saved sentence in the same session
    Given the Danki add-on is installed in an isolated Anki Desktop profile
    And deck "Latin" contains text unit "lesson-1" with text "Prima. Secunda. Tertia."
    When the pupil activates in-text help
    Then Anki shows the in-text help decks view
    When the pupil expands deck "Latin"
    Then Anki shows text unit "lesson-1" in deck "Latin"
    When the pupil opens text unit "lesson-1" in deck "Latin"
    Then Anki shows the sentence view with the sentence "Prima."
    When the pupil clicks the "Next" button
    Then Anki shows the sentence view with the sentence "Secunda."
    When the pupil clicks the "Back to decks" button
    Then Anki shows the in-text help decks view
    When the pupil opens text unit "lesson-1" in deck "Latin"
    Then Anki shows the sentence view with the sentence "Secunda."

  Scenario: The pupil selects notes-only and ambiguous surface-form help
    Given the Danki add-on is installed in an isolated Anki Desktop profile
    And deck "Latin" contains text unit "help-1" with described forms
      | surface form | headwords | notes                     |
      | quid         |           | An interrogative pronoun. |
      | amat         | amo,amare |                           |
    And vocabulary note "amo" exists in deck "Latin" with meaning "I love"
    And vocabulary note "amare" exists in deck "Latin" with meaning "to love"
    When the pupil activates in-text help
    And the pupil expands deck "Latin"
    And the pupil opens text unit "help-1" in deck "Latin"
    Then Anki shows the sentence view with the sentence "quid amat."
    When the pupil clicks the described form "QUID"
    Then Anki shows notes "An interrogative pronoun."
    When the pupil clicks the described form "amat"
    Then Anki shows candidate headwords "amo, amare"
    When the pupil chooses candidate "amare"
    Then Anki shows the vocabulary entry for "amare" with meaning "to love"

  Scenario: Missing and duplicate headwords produce visible lookup errors
    Given the Danki add-on is installed in an isolated Anki Desktop profile
    And deck "Latin" contains text unit "errors-1" with described forms
      | surface form | headwords | notes |
      | ignotum      | absent   |       |
      | duplicatum   | duplicate |      |
    And vocabulary note "duplicate" exists in deck "Latin" with meaning "first"
    And vocabulary note "duplicate" exists in deck "Latin" with meaning "second"
    When the pupil activates in-text help
    And the pupil expands deck "Latin"
    And the pupil opens text unit "errors-1" in deck "Latin"
    When the pupil clicks the described form "ignotum"
    And the pupil chooses candidate "absent"
    Then Anki shows the lookup error "No vocabulary note for headword 'absent' was found in this deck or its parent decks."
    When the pupil clicks the described form "duplicatum"
    And the pupil chooses candidate "duplicate"
    Then Anki shows the lookup error "Headword 'duplicate' matches multiple vocabulary notes in deck 'Latin'."
