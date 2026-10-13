Feature: Import and browse text units

  Scenario: A deck with no text units has an empty list
    Given a fresh text-learning service
    And the pupil has selected deck "latin"
    When the pupil views its text units
    Then deck "latin" contains no text units

  Scenario: Re-import updates the text unit in the selected deck
    Given a fresh text-learning service
    And the pupil has selected deck "latin"
    And the text-unit JSON document lesson-1:
      """
      {"schemaVersion":1,"textIdentifier":"lesson-1","text":"Arma virumque cano.","vocabularyEntries":[{"surfaceForm":"arma","headwords":["arma"]}]}
      """
    And the text-unit JSON document lesson-1-corrected:
      """
      {"schemaVersion":1,"textIdentifier":"lesson-1","text":"Arma virumque canō.","vocabularyEntries":[{"surfaceForm":"canō","headwords":["cano"]}]}
      """
    When the pupil imports the document lesson-1
    And the pupil imports the document lesson-1-corrected
    Then the last import succeeds
    And deck "latin" contains exactly these text units:
      | lesson-1-corrected |

  Scenario: The same text identifier is independent across decks
    Given a fresh text-learning service
    And the pupil has selected deck "latin"
    And the text-unit JSON document lesson-1-greek:
      """
      {"schemaVersion":1,"textIdentifier":"lesson-1","text":"Arma bona.","vocabularyEntries":[{"surfaceForm":"bona","headwords":["bonus"]}]}
      """
    And the document lesson-1-greek is already stored in deck "greek"
    And the text-unit JSON document lesson-1-latin:
      """
      {"schemaVersion":1,"textIdentifier":"lesson-1","text":"Arma virumque.","vocabularyEntries":[{"surfaceForm":"arma","headwords":["arma"]}]}
      """
    When the pupil imports the document lesson-1-latin
    Then deck "latin" contains exactly these text units:
      | lesson-1-latin |
    And deck "greek" contains exactly these text units:
      | lesson-1-greek |

  Scenario: Invalid imports return an error without storing a text unit
    Given a fresh text-learning service
    And the pupil has selected deck "latin"
    And the text-unit JSON document invalid-lesson:
      """
      {"schemaVersion":1,"textIdentifier":"lesson-1","text":"arma","vocabularyEntries":"invalid"}
      """
    When the pupil imports the document invalid-lesson
    Then the last import returns an error
    And deck "latin" contains no text units
