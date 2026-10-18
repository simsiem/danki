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
