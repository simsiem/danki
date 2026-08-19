CONTEXT — Danki domain glossary
================================

This file contains the canonical domain terms for the Danki project. Each term is defined without implementation details.


Base language
-------------

homework-driven workflow:
    A workflow where students report teacher-assigned homework and scheduled tests to the app (teachers remain
    external actors). Homework and test-preparation items are high-priority inputs that can preempt routine
    spaced-repetition scheduling. Vocabulary entries in learning phase are considered homework and must be
    completed as part of the homework; reviews of previously learned items may be delayed to accommodate
    homework.

    Rationale: Use *homework-driven workflow* as the canonical term because it emphasises that students bring
    teacher assignments into the app and that these items take precedence over normal review scheduling.
    Teachers are considered external sources of assignments and are not assumed to interact directly with the
    app.

vocabulary entry:
    The canonical unit representing everything a student should learn together for one dictionary headword:
    headword, surface form(s), pronunciation/audio, translations (both directions), short example phrase(s).
    etc. Progress and mastery are recorded at the *vocabulary entry* level.

vocabulary:
    A collection of *vocabulary entry* objects. Examples include *homework vocabulary*, *deck vocabulary*, and
    *mastered vocabulary*.

surface form:
    A specific orthographic or inflected form that appears in texts or speech (e.g., "went", "gehen", plural
    forms, conjugated forms). Surface forms are what students must recognise in context and produce.

headword:
    The canonical dictionary entry used for indexing and lookups (for example, an infinitive for verbs or
    singular nominative for nouns). The *headword* acts as the canonical key for a *vocabulary entry*.

in-text help:
    A student-facing feature that presents a source text sentence-by-sentence and allows the student to
    request assistance for specific words or phrases while working the text. The feature speeds up text work
    by revealing translations, pronunciations, or hints on demand.

auto-review from in-text help:
    A user-facing feature label for the automatic workflow that converts documented *help events* (words for
    which the student requested help) into review candidates. In context, the short form *auto-review* is
    allowed.

help event:
    A domain event recorded when a student requests assistance for a specific *surface form* while using
    *in-text help*. A *help event* includes *vocabulary entry*, the specific *surface form*, and a review
    rating (*Again*, *Hard*, *Good*)


Fields of a vocabulary entry
----------------------------

A small glossary of the field names used when a *vocabulary entry* is exported to or stored in an Anki Note.
Each list item defines the field name together with its intended use.

Headword:
    Required. The canonical sort/index label for the vocabulary entry (for example, an infinitive for verbs or
    a disambiguated form such as "cum (Konj)" vs "cum (Subj)"). Used for ordering and filtering.

FullFormDisplay:
    Required. The foreign-language presentation text shown to learners. Preserves diacritics and formatting.
    Examples: "vidēre, vīdī, vīsum", "cum (m. Abl.)".

FullFormNormalized:
    Required. A normalized variant of *FullFormDisplay* used for answer-checking and local search.
    Normalization uses Unicode NFKD decomposition and strips combining marks (diacritics). Examples: "videre,
    vidi, visum", "cum m. Abl.".

Meanings:
    Required. An ordered list of native-language senses or glosses for the entry. Short, student-facing
    translations suitable for display on the card back. Several meanings are separated with "," or ";"."

PartOfSpeech:
    A short, controlled part-of-speech tag for filtering and analytics (for example: Adverb, Präposition,
    Nomen, Verb, Adjektiv).

NotesForeign:
    A free-text, human-readable notes field shown along with the *FullFormDisplay*. It can contain student
    comments, usage hints, or any information that does not fit structured fields. Kept intentionally
    unstructured to simplify card authoring.

NotesNative:
    A free-text, human-readable notes field shown along with *Meanings*. It can contain student comments,
    usage hints, or any information that does not fit structured fields. Kept intentionally unstructured to
    simplify card authoring.

MnemonicHint:
    A short memory aid or cue shown on the card back to help retrieval. Kept concise.

PronunciationText:
    Free-text pronunciation guidance. IPA is a recommended format but not required; other phonetic
    descriptions are allowed.

AudioUrl:
    URL pointing to an audio recording for the entry (used for playback on cards).

ReferenceBook:
    School book title or identifier used for filtering and organizing homework decks.

ReferenceSection:
    Section, lesson or unit identifier within *ReferenceBook* used for finer-grained filtering.

Exercise1Front:
    First exercise slot: Holds the prompt shown to the student.

Exercise1Back:
    First exercise slot. Holds the expected answer.

Exercise2Front:
    Second exercise slot: Holds the prompt shown to the student.

Exercise2Back:
    Second exercise slot. Holds the expected answer.

Exercise3Front:
    Third exercise slot: Holds the prompt shown to the student.

Exercise3Back:
    Third exercise slot. Holds the expected answer.

Tags:
    Anki offers *Tags* as a special field. It can be imported and exported, too.