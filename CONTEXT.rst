CONTEXT — Danki domain glossary
================================

This file contains the canonical domain terms for the Danki project. Each term is defined without implementation details.

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
