Feature: Select authored surface forms and resolve headwords

  Scenario: Only described surface forms are selectable and longer overlaps win
    Given a fresh text-learning service
    And text unit "reading" in deck "child" has sentence "PORTA MAGNA; porta; extra." and descriptions:
      | surface form | headwords | notes |
      | porta        | porta    |       |
      | porta magna  | magnus   |       |
    When the pupil views selectable forms in sentence 0 of "reading"
    Then the selectable occurrences are:
      | surface form | matched text |
      | porta magna  | PORTA MAGNA |
      | porta        | porta       |

  Scenario: Selecting notes-only help returns the authored notes
    Given a fresh text-learning service
    And text unit "reading" in deck "child" has sentence "quid?" and descriptions:
      | surface form | headwords | notes                     |
      | quid         |          | An interrogative pronoun. |
    When the pupil selects "QUID" in sentence 0 of "reading"
    Then the selected help contains notes "An interrogative pronoun."

  Scenario: Undescribed words cannot be selected
    Given a fresh text-learning service
    And text unit "reading" in deck "child" has sentence "quid est." and descriptions:
      | surface form | headwords | notes |
      | quid         |          | note  |
    When the pupil selects "est" in sentence 0 of "reading"
    Then surface-form selection fails with "The surface form is not selectable in the current sentence."

  Scenario: Selecting an ambiguous form exposes every candidate
    Given a fresh text-learning service
    And text unit "reading" in deck "child" has sentence "amat." and descriptions:
      | surface form | headwords | notes |
      | amat         | amo,amo2  |       |
    When the pupil selects "amat" in sentence 0 of "reading"
    Then the selected help offers headwords "amo, amo2"

  Scenario: Headword lookup searches the nearest deck before its parent
    Given a fresh text-learning service
    And deck "child" has parent deck "parent"
    And vocabulary note "amo" exists in deck "parent" with meaning "love"
    And vocabulary note "amo" exists in deck "child" with meaning "I love"
    When the pupil resolves headword "amo" from deck "child"
    Then the resolved vocabulary entry is in deck "child" with meaning "I love"

  Scenario: Headword lookup searches parent decks from nearest to farthest
    Given a fresh text-learning service
    And deck "child" has parent deck "parent"
    And deck "parent" has parent deck "grandparent"
    And vocabulary note "sum" exists in deck "grandparent" with meaning "I am"
    And vocabulary note "sum" exists in deck "parent" with meaning "you are"
    When the pupil resolves headword "sum" from deck "child"
    Then the resolved vocabulary entry is in deck "parent" with meaning "you are"

  Scenario: Headword lookup distinguishes case
    Given a fresh text-learning service
    And vocabulary note "Sol" exists in deck "child" with meaning "the sun"
    When the pupil resolves headword "sol" from deck "child"
    Then headword resolution fails with "No vocabulary note for headword 'sol' was found in this deck or its parent decks."

  Scenario: A duplicate exact headword in the nearest deck is an error
    Given a fresh text-learning service
    And vocabulary note "amo" exists in deck "child" with meaning "love"
    And vocabulary note "amo" exists in deck "child" with meaning "I love"
    When the pupil resolves headword "amo" from deck "child"
    Then headword resolution fails with "Headword 'amo' matches multiple vocabulary notes in deck 'child'."