Feature: Versioned text-unit JSON

  Scenario: Import and export a version-one text unit without losing information
    Given a fresh text-learning service
    And the pupil has selected deck "latin"
    And the text-unit JSON document lesson-1:
      """
      {"schemaVersion":1,"textIdentifier":"lesson-1","text":"Arma virumque cano.","vocabularyEntries":[{"surfaceForm":"arma","headwords":["arma"]},{"surfaceForm":"cano","notes":"first-person singular"}]}
      """
    When the pupil imports the document lesson-1
    And the pupil exports the current text unit as document lesson-1-export
    Then document lesson-1-export matches document lesson-1

  Scenario Outline: Reject malformed text-unit documents
    Given a fresh text-learning service
    And the pupil has selected deck "latin"
    And the text-unit JSON document malformed-input:
      """
      <document>
      """
    When the pupil imports the document malformed-input
    Then the last import returns an error

    Examples:
      | document                                                                                                                                                                                  |
      | {"schemaVersion":2,"textIdentifier":"lesson-1","text":"arma","vocabularyEntries":[]}                                                                                                 |
      | {"textIdentifier":"lesson-1","text":"arma","vocabularyEntries":[]}                                                                                                                 |
      | {"schemaVersion":true,"textIdentifier":"lesson-1","text":"arma","vocabularyEntries":[]}                                                                                          |
      | {"schemaVersion":1,"textIdentifier":"lesson-1","text":"arma","vocabularyEntries":[],"extra":true}                                                                                |
      | {"schemaVersion":1,"textIdentifier":"lesson-1","text":"arma","vocabularyEntries":[{"surfaceForm":"arma","headwords":["arma"],"notes":"extra"}]}                             |
      | {"schemaVersion":1,"textIdentifier":"lesson-1","text":"arma","vocabularyEntries":[{"surfaceForm":"arma","headwords":["arma"],"extra":true}]}                               |
      | {"schemaVersion":1,"textIdentifier":"lesson-1","text":"arma","vocabularyEntries":[{"surfaceForm":"arma"}]}                                                                       |
      | {"schemaVersion":1,"textIdentifier":"lesson-1","text":"arma","vocabularyEntries":[{"surfaceForm":"arma","headwords":["arma"]},{"surfaceForm":"ARMA","notes":"note"}]} |
      | {"schemaVersion":1,"textIdentifier":"lesson-1","text":"caf\u00e9","vocabularyEntries":[{"surfaceForm":"caf\u00e9","headwords":["café"]},{"surfaceForm":"cafe\u0301","notes":"note"}]} |
      | {"schemaVersion":1,"textIdentifier":"lesson-1","text":"arma","vocabularyEntries":[{"surfaceForm":"ignotum","notes":"unknown"}]}                                            |
