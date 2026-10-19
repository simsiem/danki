from __future__ import annotations

import json
from typing import TYPE_CHECKING, NoReturn

from anki.collection import Collection  # noqa: TC002
from anki.decks import DeckId
from anki.models import NotetypeDict, NotetypeId

from danki.textunit import ResolvedVocabularyEntry, TextUnit, _TextUnitCodec

if TYPE_CHECKING:
    from anki.cards import Card
    from anki.dbproxy import DBProxy
    from anki.notes import Note, NoteId

STORAGE_NOTE_TYPE_NAME = "Danki Text Unit"
_FIELD_NAMES = ("TextIdentifier", "Text", "VocabularyEntries")
_TEMPLATE_NAME = "Danki Text Unit Storage"
_POSITION_CUSTOM_DATA_KEY = "danki"


class AnkiTextUnitStorageError(RuntimeError):
    DUPLICATE_TEXT_IDENTIFIERS = "Duplicate text identifiers exist in the selected deck."
    INVALID_CUSTOM_DATA = "The storage card contains invalid custom data."
    CUSTOM_DATA_MUST_BE_OBJECT = "The storage card custom data must be an object."
    UNSUPPORTED_READING_POSITION = "The storage card contains an unsupported reading position."
    NO_UNIQUE_STORAGE_CARD = "The text unit has no unique storage card in the selected deck."
    INVALID_STORAGE_CARD_COUNT = "The text unit does not have exactly one storage card."


def _raise_storage_error(message: str) -> NoReturn:
    raise AnkiTextUnitStorageError(message)


class AnkiTextUnitStorage:
    def __init__(self, collection: Collection) -> None:
        self._collection = collection
        self._note_type = self._ensure_note_type()

    def list_text_units(self, deck_id: str) -> tuple[TextUnit, ...]:
        anki_deck_id = DeckId(int(deck_id))
        note_ids = self._note_ids_in_deck(anki_deck_id)
        return tuple(self._read_text_unit(note_id) for note_id in note_ids)

    def upsert_text_unit(self, deck_id: str, text_unit: TextUnit) -> None:
        anki_deck_id = DeckId(int(deck_id))
        matches = self._matching_text_unit_notes(anki_deck_id, text_unit.text_identifier)
        if len(matches) > 1:
            _raise_storage_error("Duplicate text identifiers exist in the selected deck.")

        if matches:
            note = matches[0]
            self._write_text_unit(note, text_unit)
            self._collection.update_note(note)
        else:
            note = self._collection.new_note(self._note_type)
            self._write_text_unit(note, text_unit)
            self._collection.add_note(note, anki_deck_id)

        card_ids = note.card_ids()
        self._collection.sched.suspend_cards(card_ids)

    def get_sentence_position(self, deck_id: str, text_identifier: str) -> int:
        card = self._storage_card(deck_id, text_identifier)
        try:
            custom_data = json.loads(card.custom_data or "{}")
        except json.JSONDecodeError as error:
            raise AnkiTextUnitStorageError(AnkiTextUnitStorageError.INVALID_CUSTOM_DATA) from error
        if not isinstance(custom_data, dict):
            raise AnkiTextUnitStorageError(AnkiTextUnitStorageError.CUSTOM_DATA_MUST_BE_OBJECT)
        position_data = custom_data.get(_POSITION_CUSTOM_DATA_KEY)
        if position_data is None:
            return 0
        if (
            not isinstance(position_data, dict)
            or position_data.get("version") != 1
            or type(position_data.get("sentenceIndex")) is not int
            or position_data["sentenceIndex"] < 0
        ):
            raise AnkiTextUnitStorageError(AnkiTextUnitStorageError.UNSUPPORTED_READING_POSITION)
        return position_data["sentenceIndex"]

    def set_sentence_position(self, deck_id: str, text_identifier: str, position: int) -> None:
        if position < 0:
            message = "A sentence position cannot be negative."
            raise ValueError(message)
        card = self._storage_card(deck_id, text_identifier)
        try:
            custom_data = json.loads(card.custom_data or "{}")
        except json.JSONDecodeError as error:
            raise AnkiTextUnitStorageError(AnkiTextUnitStorageError.INVALID_CUSTOM_DATA) from error
        if not isinstance(custom_data, dict):
            raise AnkiTextUnitStorageError(AnkiTextUnitStorageError.CUSTOM_DATA_MUST_BE_OBJECT)
        custom_data[_POSITION_CUSTOM_DATA_KEY] = {"version": 1, "sentenceIndex": position}
        card.custom_data = json.dumps(custom_data, ensure_ascii=False, separators=(",", ":"))
        self._collection.update_card(card, skip_undo_entry=True)

    def parent_deck_ids(self, deck_id: str) -> tuple[str, ...]:
        parents = self._collection.decks.parents(DeckId(int(deck_id)))
        return tuple(str(parent["id"]) for parent in reversed(parents))

    def deck_name(self, deck_id: str) -> str:
        return self._collection.decks.name(DeckId(int(deck_id)))

    def find_vocabulary_entries(self, deck_id: str, headword: str) -> tuple[ResolvedVocabularyEntry, ...]:
        anki_deck_id = DeckId(int(deck_id))
        note_ids = self._database().list(
            """
            select distinct notes.id
            from notes join cards on cards.nid = notes.id
            where cards.did = ? and notes.mid != ?
            order by notes.id
            """,
            anki_deck_id,
            self._note_type["id"],
        )
        matches: list[ResolvedVocabularyEntry] = []
        for note_id in note_ids:
            note = self._collection.get_note(note_id)
            if "Headword" not in note or note["Headword"] != headword:
                continue
            note_type = self._collection.models.get(NotetypeId(note.mid))
            if note_type is None:
                _raise_storage_error("Anki could not load a vocabulary note type.")
            fields = tuple(
                (field_name, note[field_name])
                for field_name in self._collection.models.field_names(note_type)
            )
            matches.append(ResolvedVocabularyEntry(str(anki_deck_id), headword, fields))
        return tuple(matches)

    def _storage_card(self, deck_id: str, text_identifier: str) -> Card:
        anki_deck_id = DeckId(int(deck_id))
        matches = self._matching_text_unit_notes(anki_deck_id, text_identifier)
        if len(matches) != 1:
            raise AnkiTextUnitStorageError(AnkiTextUnitStorageError.NO_UNIQUE_STORAGE_CARD)
        card_ids = matches[0].card_ids()
        if len(card_ids) != 1:
            raise AnkiTextUnitStorageError(AnkiTextUnitStorageError.INVALID_STORAGE_CARD_COUNT)
        return self._collection.get_card(card_ids[0])

    def _matching_text_unit_notes(self, deck_id: DeckId, text_identifier: str) -> list[Note]:
        matches = []
        for note_id in self._note_ids_in_deck(deck_id):
            note = self._collection.get_note(note_id)
            if note["TextIdentifier"] == text_identifier:
                matches.append(note)
        return matches

    def _ensure_note_type(self) -> NotetypeDict:
        note_type = self._collection.models.by_name(STORAGE_NOTE_TYPE_NAME)
        if note_type is None:
            note_type = self._collection.models.new(STORAGE_NOTE_TYPE_NAME)
            for field_name in _FIELD_NAMES:
                self._collection.models.add_field(
                    note_type,
                    self._collection.models.new_field(field_name),
                )
            template = self._collection.models.new_template(_TEMPLATE_NAME)
            template["qfmt"] = "{{TextIdentifier}}"
            template["afmt"] = "{{TextIdentifier}}"
            self._collection.models.add_template(note_type, template)
            note_type["sortf"] = 0
            result = self._collection.models.add_dict(note_type)
            note_type = self._collection.models.get(NotetypeId(result.id))

        if note_type is None:
            _raise_storage_error("Anki did not create the managed text-unit note type.")
        if self._collection.models.field_names(note_type) != list(_FIELD_NAMES):
            _raise_storage_error("The managed text-unit note type has unexpected fields.")
        if len(note_type["tmpls"]) != 1:
            _raise_storage_error("The managed text-unit note type must have one storage card template.")
        if note_type["sortf"] != 0:
            note_type["sortf"] = 0
            self._collection.models.update_dict(note_type)
            note_type = self._collection.models.get(NotetypeId(note_type["id"]))
            if note_type is None:
                _raise_storage_error("Anki could not reload the managed text-unit note type.")
        return note_type

    def _note_ids_in_deck(self, deck_id: DeckId) -> list[NoteId]:
        db = self._database()
        return db.list(
            """
            select distinct notes.id
            from notes join cards on cards.nid = notes.id
            where notes.mid = ? and cards.did = ?
            order by notes.id
            """,
            self._note_type["id"],
            deck_id,
        )

    def _database(self) -> DBProxy:
        database = self._collection.db
        if database is None:
            _raise_storage_error("The Anki collection is not open.")
        return database

    def _read_text_unit(self, note_id: NoteId) -> TextUnit:
        note = self._collection.get_note(note_id)
        document = json.dumps(
            {
                "schemaVersion": 1,
                "textIdentifier": note["TextIdentifier"],
                "text": note["Text"],
                "vocabularyEntries": json.loads(note["VocabularyEntries"]),
            },
            ensure_ascii=False,
        )
        return _TextUnitCodec.loads(document)

    @staticmethod
    def _write_text_unit(note: Note, text_unit: TextUnit) -> None:
        document = json.loads(_TextUnitCodec.dumps(text_unit))
        note["TextIdentifier"] = text_unit.text_identifier
        note["Text"] = text_unit.text
        note["VocabularyEntries"] = json.dumps(document["vocabularyEntries"], ensure_ascii=False)
