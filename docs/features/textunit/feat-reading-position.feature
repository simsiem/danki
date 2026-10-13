Feature: Resume and navigate text-unit sentences

  Scenario: Opening a text unit resumes its saved sentence
    Given a fresh text-learning service
    And the pupil has selected deck "latin"
    And text unit lesson-1 is stored with text:
      """
      Prima. Secunda. Tertia.
      """
    And the saved sentence position for lesson-1 is 1
    When the pupil opens text unit lesson-1
    Then the current sentence is "Secunda."

  Scenario: The pupil navigates sentences and can restart
    Given a fresh text-learning service
    And the pupil has selected deck "latin"
    And text unit lesson-1 is stored with text:
      """
      Prima. Secunda. Tertia.
      """
    When the pupil opens text unit lesson-1
    And the pupil moves to the next sentence
    Then the current sentence is "Secunda."
    When the pupil moves to the previous sentence
    Then the current sentence is "Prima."
    When the pupil moves to the previous sentence
    Then the current sentence is "Prima."
    When the pupil moves to the next sentence
    And the pupil moves to the next sentence
    Then the current sentence is "Tertia."
    When the pupil restarts the text
    Then the current sentence is "Prima."

  Scenario: Navigation saves the current position and stops at the final sentence
    Given a fresh text-learning service
    And the pupil has selected deck "latin"
    And text unit lesson-1 is stored with text:
      """
      Prima. Secunda.
      """
    When the pupil opens text unit lesson-1
    And the pupil moves to the next sentence
    And the pupil moves to the next sentence
    Then the current sentence is "Secunda."
    When the pupil reopens text unit lesson-1
    Then the current sentence is "Secunda."

  Scenario Outline: Sentence boundaries preserve punctuation and normalize line breaks
    Given a fresh text-learning service
    And the pupil has selected deck "latin"
    And text unit lesson-1 is stored with text:
      """
      <text>
      """
    When the pupil opens text unit lesson-1
    Then the sentences are:
      | sentence   |
      | <sentence1> |
      | <sentence2> |

    Examples:
      | text                         | sentence1       | sentence2 |
      | "Salve!"\nQuid agis?        | "Salve!"        | Quid agis? |
      | ¿Qué tal?\n¡Muy bien!        | ¿Qué tal?       | ¡Muy bien! |
      | Prima\nsecunda. Tertia       | Prima secunda.  | Tertia |

  Scenario: Empty text opens without a current sentence
    Given a fresh text-learning service
    And the pupil has selected deck "latin"
    And text unit lesson-1 is stored with empty text
    When the pupil opens text unit lesson-1
    Then the current sentence is empty

  Scenario: Updating a text clamps a stale position to its final sentence
    Given a fresh text-learning service
    And the pupil has selected deck "latin"
    And text unit lesson-1 is stored with text:
      """
      Prima. Secunda. Tertia.
      """
    And the saved sentence position for lesson-1 is 2
    When the pupil updates text unit lesson-1 with text:
      """
      Una.
      """
    And the pupil opens text unit lesson-1
    Then the current sentence is "Una."
