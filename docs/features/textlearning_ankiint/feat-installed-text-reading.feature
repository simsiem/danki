Feature: Read text units through the installed Anki Desktop add-on

  Scenario: Closing and reopening a text resumes the saved sentence in the same session
    Given the standalone add-on is installed in an isolated Anki Desktop profile
    And deck "Latin" contains text unit "lesson-1" with text "Prima. Secunda. Tertia."
    When the pupil opens "lesson-1" in deck "Latin", advances a sentence, closes it, and reopens it
    Then the initial reading dialog displayed "Prima."
    And navigation displayed "Secunda."
    And the reopened reading dialog displayed "Secunda."
