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
    "SentenceReading",
    "TextLearning",
    "TextUnit",
    "TextUnitStorage",
    "VocabularyDescription",
]


@dataclass(frozen=True)
class VocabularyDescription:
    surface_form: str
    headwords: tuple[str, ...] | None = None
    notes: str | None = None


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


class TextLearning:
    def __init__(self, storage: TextUnitStorage, positions: ReadingPositionStorage) -> None:
        self._storage = storage
        self._positions = positions

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

    def open_text_unit(
        self, deck_id: str, text_identifier: str
    ) -> tuple[SentenceReading | None, str | None]:
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

        sentences = _split_sentences(matches[0].text)
        saved_position = self._positions.get_sentence_position(deck_id, text_identifier)
        sentence_index = min(max(saved_position, 0), max(len(sentences) - 1, 0))
        if sentence_index != saved_position:
            self._positions.set_sentence_position(deck_id, text_identifier, sentence_index)
        return SentenceReading(text_identifier, sentences, sentence_index), None

    def next_sentence(
        self, deck_id: str, text_identifier: str
    ) -> tuple[SentenceReading | None, str | None]:
        return self._move_to_sentence(deck_id, text_identifier, step=1)

    def previous_sentence(
        self, deck_id: str, text_identifier: str
    ) -> tuple[SentenceReading | None, str | None]:
        return self._move_to_sentence(deck_id, text_identifier, step=-1)

    def restart_text(
        self, deck_id: str, text_identifier: str
    ) -> tuple[SentenceReading | None, str | None]:
        return self._move_to_sentence(deck_id, text_identifier, step=None)

    def _move_to_sentence(
        self, deck_id: str, text_identifier: str, step: int | None
    ) -> tuple[SentenceReading | None, str | None]:
        reading, error = self.open_text_unit(deck_id, text_identifier)
        if error is not None or reading is None:
            return None, error
        final_index = max(len(reading.sentences) - 1, 0)
        if step is None:
            sentence_index = 0
        else:
            sentence_index = min(max(reading.sentence_index + step, 0), final_index)
        self._positions.set_sentence_position(deck_id, text_identifier, sentence_index)
        return SentenceReading(text_identifier, reading.sentences, sentence_index), None


def _split_sentences(text: str) -> tuple[str, ...]:
    normalized_text = re.sub(r"\s+", " ", text).strip()
    if not normalized_text:
        return ()

    sentences: list[str] = []
    fragment_start = 0
    ending = re.compile(r"[.!?。！？؟｡։।…]+[\"'’”»›)\]}）】」』]*")
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


class _TextUnitImportError(ValueError):
    pass


def _raise_import_error(message: str) -> NoReturn:
    raise _TextUnitImportError(message)


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
        normalized_text = _TextUnitCodec._normalize_surface_form(data["text"])
        for description in descriptions:
            normalized = _TextUnitCodec._normalize_surface_form(description.surface_form)
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

    @staticmethod
    def _normalize_surface_form(value: str) -> str:
        normalized = unicodedata.normalize("NFC", value).casefold()
        return re.sub(r"\s+", " ", normalized).strip()
