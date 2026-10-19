"""Public text-learning interface and its core implementation.

Consumers use ``TextLearning`` with the domain and storage types below. JSON
encoding and validation are implementation details of this module.
"""

import json
import re
import unicodedata
from dataclasses import dataclass
from typing import NoReturn, Protocol

__all__ = [
    "ReadingPositionStorage",
    "ResolvedVocabularyEntry",
    "SentenceReading",
    "SurfaceFormOccurrence",
    "TextLearning",
    "TextUnit",
    "TextUnitStorage",
    "VocabularyDescription",
    "VocabularyLookupStorage",
]


@dataclass(frozen=True)
class VocabularyDescription:
    surface_form: str
    headwords: tuple[str, ...] | None = None
    notes: str | None = None


@dataclass(frozen=True)
class SurfaceFormOccurrence:
    surface_form: str
    start: int
    end: int
    matched_text: str


@dataclass(frozen=True)
class ResolvedVocabularyEntry:
    deck_id: str
    headword: str
    fields: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class TextUnit:
    text_identifier: str
    text: str
    vocabulary_entries: tuple[VocabularyDescription, ...]


@dataclass(frozen=True)
class SentenceReading:
    text_identifier: str
    sentences: tuple[str, ...]
    sentence_index: int

    @property
    def current_sentence(self) -> str:
        if not self.sentences:
            return ""
        return self.sentences[self.sentence_index]


class TextUnitStorage(Protocol):
    def list_text_units(self, deck_id: str) -> tuple[TextUnit, ...]: ...

    def upsert_text_unit(self, deck_id: str, text_unit: TextUnit) -> None: ...


class ReadingPositionStorage(Protocol):
    def get_sentence_position(self, deck_id: str, text_identifier: str) -> int: ...

    def set_sentence_position(self, deck_id: str, text_identifier: str, position: int) -> None: ...


class VocabularyLookupStorage(Protocol):
    def parent_deck_ids(self, deck_id: str) -> tuple[str, ...]: ...

    def find_vocabulary_entries(self, deck_id: str, headword: str) -> tuple[ResolvedVocabularyEntry, ...]: ...

    def deck_name(self, deck_id: str) -> str: ...


class TextLearning:
    def __init__(
        self,
        storage: TextUnitStorage,
        positions: ReadingPositionStorage,
        vocabulary: VocabularyLookupStorage | None = None,
    ) -> None:
        self._storage = storage
        self._positions = positions
        self._vocabulary = vocabulary

    def list_text_units(self, deck_id: str) -> tuple[tuple[TextUnit, ...] | None, str | None]:
        if not deck_id:
            return None, "A deck must be selected."
        return self._storage.list_text_units(deck_id), None

    def import_text_unit(self, deck_id: str, document: str) -> tuple[TextUnit | None, str | None]:
        if not deck_id:
            return None, "A deck must be selected."
        try:
            text_unit = _TextUnitCodec.loads(document)
        except _TextUnitImportError as error:
            return None, str(error)
        self._storage.upsert_text_unit(deck_id, text_unit)
        return text_unit, None

    @staticmethod
    def export_text_unit(text_unit: TextUnit) -> str:
        return _TextUnitCodec.dumps(text_unit)

    def open_text_unit(self, deck_id: str, text_identifier: str) -> tuple[SentenceReading | None, str | None]:
        text_unit, error = self._get_text_unit(deck_id, text_identifier)
        if error is not None or text_unit is None:
            return None, error
        sentences = _split_sentences(text_unit.text)
        saved_position = self._positions.get_sentence_position(deck_id, text_identifier)
        sentence_index = min(max(saved_position, 0), max(len(sentences) - 1, 0))
        if sentence_index != saved_position:
            self._positions.set_sentence_position(deck_id, text_identifier, sentence_index)
        return SentenceReading(text_identifier, sentences, sentence_index), None

    def next_sentence(self, deck_id: str, text_identifier: str) -> tuple[SentenceReading | None, str | None]:
        return self._move_to_sentence(deck_id, text_identifier, step=1)

    def previous_sentence(
        self, deck_id: str, text_identifier: str
    ) -> tuple[SentenceReading | None, str | None]:
        return self._move_to_sentence(deck_id, text_identifier, step=-1)

    def restart_text(self, deck_id: str, text_identifier: str) -> tuple[SentenceReading | None, str | None]:
        return self._move_to_sentence(deck_id, text_identifier, step=None)

    def surface_forms_for_sentence(
        self, deck_id: str, text_identifier: str, sentence_index: int
    ) -> tuple[tuple[SurfaceFormOccurrence, ...] | None, str | None]:
        text_unit, error = self._get_text_unit(deck_id, text_identifier)
        if error is not None or text_unit is None:
            return None, error
        sentences = _split_sentences(text_unit.text)
        if sentence_index < 0 or sentence_index >= len(sentences):
            return None, "The sentence position is outside the text unit."
        return _surface_form_occurrences(sentences[sentence_index], text_unit.vocabulary_entries), None

    def select_surface_form(
        self, deck_id: str, text_identifier: str, sentence_index: int, surface_form: str
    ) -> tuple[VocabularyDescription | None, str | None]:
        occurrences, error = self.surface_forms_for_sentence(deck_id, text_identifier, sentence_index)
        if error is not None or occurrences is None:
            return None, error
        normalized_form = _normalize_surface_form(surface_form)
        if not any(
            _normalize_surface_form(occurrence.surface_form) == normalized_form for occurrence in occurrences
        ):
            return None, "The surface form is not selectable in the current sentence."
        text_unit, error = self._get_text_unit(deck_id, text_identifier)
        if error is not None or text_unit is None:
            return None, error
        description = next(
            item
            for item in text_unit.vocabulary_entries
            if _normalize_surface_form(item.surface_form) == normalized_form
        )
        return description, None

    def resolve_headword(
        self, deck_id: str, headword: str
    ) -> tuple[ResolvedVocabularyEntry | None, str | None]:
        if not deck_id:
            return None, "A deck must be selected."
        if self._vocabulary is None:
            return None, "Vocabulary lookup is unavailable."
        for search_deck_id in (deck_id, *self._vocabulary.parent_deck_ids(deck_id)):
            matches = self._vocabulary.find_vocabulary_entries(search_deck_id, headword)
            if len(matches) > 1:
                deck_name = self._vocabulary.deck_name(search_deck_id)
                return None, f"Headword '{headword}' matches multiple vocabulary notes in deck '{deck_name}'."
            if matches:
                return matches[0], None
        return (
            None,
            f"No vocabulary note for headword '{headword}' was found in this deck or its parent decks.",
        )

    def _get_text_unit(self, deck_id: str, text_identifier: str) -> tuple[TextUnit | None, str | None]:
        if not deck_id:
            return None, "A deck must be selected."
        text_units, error = self.list_text_units(deck_id)
        if error is not None or text_units is None:
            return None, error
        matches = [unit for unit in text_units if unit.text_identifier == text_identifier]
        if not matches:
            return None, "The text unit does not exist in the selected deck."
        if len(matches) > 1:
            return None, "The text identifier is duplicated in the selected deck."
        return matches[0], None

    def _move_to_sentence(
        self, deck_id: str, text_identifier: str, step: int | None
    ) -> tuple[SentenceReading | None, str | None]:
        reading, error = self.open_text_unit(deck_id, text_identifier)
        if error is not None or reading is None:
            return None, error
        final_index = max(len(reading.sentences) - 1, 0)
        sentence_index = 0 if step is None else min(max(reading.sentence_index + step, 0), final_index)
        self._positions.set_sentence_position(deck_id, text_identifier, sentence_index)
        return SentenceReading(text_identifier, reading.sentences, sentence_index), None


def _split_sentences(text: str) -> tuple[str, ...]:
    normalized_text = re.sub(r"\s+", " ", text).strip()
    if not normalized_text:
        return ()

    sentences: list[str] = []
    fragment_start = 0
    ending = re.compile(r"[.!?。！？؟｡։।…]+[\"'’”»›)\]}）】」』]*")  # noqa: RUF001
    for match in ending.finditer(normalized_text):
        fragment_end = match.end()
        if fragment_end == len(normalized_text) or normalized_text[fragment_end].isspace():
            sentence = normalized_text[fragment_start:fragment_end].strip()
            if sentence:
                sentences.append(sentence)
            fragment_start = fragment_end
            while fragment_start < len(normalized_text) and normalized_text[fragment_start].isspace():
                fragment_start += 1

    final_fragment = normalized_text[fragment_start:].strip()
    if final_fragment:
        sentences.append(final_fragment)
    return tuple(sentences)


def _surface_form_occurrences(
    sentence: str, descriptions: tuple[VocabularyDescription, ...]
) -> tuple[SurfaceFormOccurrence, ...]:
    normalized_sentence, source_offsets = _normalize_with_offsets(sentence)
    candidates: list[tuple[int, int, int, VocabularyDescription]] = []
    for description_index, description in enumerate(descriptions):
        normalized_form = _normalize_surface_form(description.surface_form)
        if not normalized_form:
            continue
        search_from = 0
        while (match_start := normalized_sentence.find(normalized_form, search_from)) >= 0:
            match_end = match_start + len(normalized_form)
            original_start = source_offsets[match_start][0]
            original_end = source_offsets[match_end - 1][1]
            candidates.append((original_start, original_end, description_index, description))
            search_from = match_start + 1

    candidates.sort(
        key=lambda item: (
            -len(_normalize_surface_form(item[3].surface_form)),
            item[0],
            item[2],
        )
    )
    selected: list[tuple[int, int, int, VocabularyDescription]] = []
    for candidate in candidates:
        if any(candidate[0] < chosen[1] and chosen[0] < candidate[1] for chosen in selected):
            continue
        selected.append(candidate)
    selected.sort(key=lambda item: item[0])
    return tuple(
        SurfaceFormOccurrence(
            description.surface_form,
            start,
            end,
            sentence[start:end],
        )
        for start, end, _description_index, description in selected
    )


def _normalize_with_offsets(text: str) -> tuple[str, tuple[tuple[int, int], ...]]:
    normalized_characters: list[str] = []
    source_offsets: list[tuple[int, int]] = []
    source_index = 0
    while source_index < len(text):
        cluster_end = source_index + 1
        while cluster_end < len(text) and unicodedata.combining(text[cluster_end]):
            cluster_end += 1
        normalized_cluster = unicodedata.normalize("NFC", text[source_index:cluster_end]).casefold()
        for normalized_character in normalized_cluster:
            output_character = normalized_character
            if normalized_character.isspace():
                if normalized_characters and normalized_characters[-1] == " ":
                    source_offsets[-1] = (source_offsets[-1][0], cluster_end)
                    continue
                output_character = " "
            normalized_characters.append(output_character)
            source_offsets.append((source_index, cluster_end))
        source_index = cluster_end

    while normalized_characters and normalized_characters[0] == " ":
        normalized_characters.pop(0)
        source_offsets.pop(0)
    while normalized_characters and normalized_characters[-1] == " ":
        normalized_characters.pop()
        source_offsets.pop()
    return "".join(normalized_characters), tuple(source_offsets)


class _TextUnitImportError(ValueError):
    pass


def _raise_import_error(message: str) -> NoReturn:
    raise _TextUnitImportError(message)


def _normalize_surface_form(value: str) -> str:
    normalized = unicodedata.normalize("NFC", value).casefold()
    return re.sub(r"\s+", " ", normalized).strip()


class _TextUnitCodec:
    @staticmethod
    def loads(document: str) -> TextUnit:
        try:
            data = json.loads(document)
        except json.JSONDecodeError as error:
            _raise_import_error(f"Invalid text-unit JSON: {error.msg}.")

        if not isinstance(data, dict):
            _raise_import_error("A text unit must be a JSON object.")
        if set(data) != {"schemaVersion", "textIdentifier", "text", "vocabularyEntries"}:
            _raise_import_error(
                "A text unit must contain exactly schemaVersion, textIdentifier, text, and vocabularyEntries."
            )
        if type(data["schemaVersion"]) is not int or data["schemaVersion"] != 1:
            _raise_import_error("schemaVersion must be 1.")
        if not isinstance(data["textIdentifier"], str) or not data["textIdentifier"].strip():
            _raise_import_error("textIdentifier must be a non-empty string.")
        if not isinstance(data["text"], str):
            _raise_import_error("text must be a string.")
        if not isinstance(data["vocabularyEntries"], list):
            _raise_import_error("vocabularyEntries must be an array.")

        descriptions = tuple(_TextUnitCodec._description(item) for item in data["vocabularyEntries"])
        seen_surface_forms: set[str] = set()
        normalized_text = _normalize_surface_form(data["text"])
        for description in descriptions:
            normalized = _normalize_surface_form(description.surface_form)
            if normalized in seen_surface_forms:
                _raise_import_error(f"Duplicate surface form: {description.surface_form}.")
            seen_surface_forms.add(normalized)
            if normalized not in normalized_text:
                _raise_import_error(f"Surface form does not occur in text: {description.surface_form}.")

        return TextUnit(data["textIdentifier"], data["text"], descriptions)

    @staticmethod
    def dumps(text_unit: TextUnit) -> str:
        document = {
            "schemaVersion": 1,
            "textIdentifier": text_unit.text_identifier,
            "text": text_unit.text,
            "vocabularyEntries": [
                _TextUnitCodec._description_document(description)
                for description in text_unit.vocabulary_entries
            ],
        }
        return json.dumps(document, ensure_ascii=False)

    @staticmethod
    def _description(data: object) -> VocabularyDescription:
        if not isinstance(data, dict) or "surfaceForm" not in data:
            _raise_import_error("Each vocabulary entry must be an object with a surfaceForm.")
        has_headwords = "headwords" in data
        has_notes = "notes" in data
        if has_headwords == has_notes:
            _raise_import_error("Each surface form must contain exactly one of headwords or notes.")
        expected_fields = {"surfaceForm", "headwords"} if has_headwords else {"surfaceForm", "notes"}
        if set(data) != expected_fields:
            _raise_import_error("A vocabulary entry contains unknown fields.")
        surface_form = data["surfaceForm"]
        if not isinstance(surface_form, str) or not surface_form.strip():
            _raise_import_error("surfaceForm must be a non-empty string.")
        if has_headwords:
            headwords = data["headwords"]
            if (
                not isinstance(headwords, list)
                or not headwords
                or not all(isinstance(headword, str) and headword for headword in headwords)
            ):
                _raise_import_error("headwords must be a non-empty array of non-empty strings.")
            return VocabularyDescription(surface_form, tuple(headwords))
        notes = data["notes"]
        if not isinstance(notes, str):
            _raise_import_error("notes must be a string.")
        return VocabularyDescription(surface_form, notes=notes)

    @staticmethod
    def _description_document(description: VocabularyDescription) -> dict[str, object]:
        result: dict[str, object] = {"surfaceForm": description.surface_form}
        if description.headwords is not None:
            result["headwords"] = list(description.headwords)
        else:
            result["notes"] = description.notes
        return result
