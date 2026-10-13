import json
from typing import NoReturn

from anki.collection import Collection
from anki.dbproxy import DBProxy
from anki.decks import DeckId
from anki.models import NotetypeDict, NotetypeId
from anki.notes import Note, NoteId

from danki.textunit import TextUnit, _TextUnitCodec

STORAGE_NOTE_TYPE_NAME = "Danki Text Unit"
_FIELD_NAMES = ("TextIdentifier", "Text", "VocabularyEntries")
_TEMPLATE_NAME = "Danki Text Unit Storage"


class AnkiTextUnitStorageError(RuntimeError):
    pass


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
        matches = []
        for note_id in self._note_ids_in_deck(anki_deck_id):
            note = self._collection.get_note(note_id)
            if note["TextIdentifier"] == text_unit.text_identifier:
                matches.append(note)
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
