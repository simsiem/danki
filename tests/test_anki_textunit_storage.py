import pytest
from anki.collection import Collection
from anki.notes import NoteId

from danki.anki_storage import STORAGE_NOTE_TYPE_NAME, AnkiTextUnitStorage
from danki.textunit import TextUnit, VocabularyDescription


def test_collection_storage_updates_text_units_and_suspends_storage_cards(tmp_path) -> None:
    collection = Collection(str(tmp_path / "collection.anki2"))
    try:
        storage = AnkiTextUnitStorage(collection)
        db = collection.db
        if db is None:
            pytest.fail("The test collection did not open its database.")
        latin_deck_id = collection.decks.id("Latin")
        greek_deck_id = collection.decks.id("Greek")
        assert latin_deck_id is not None
        assert greek_deck_id is not None
        assert storage.list_text_units(str(latin_deck_id)) == ()

        initial = TextUnit(
            "lesson-1",
            "Arma virumque.",
            (VocabularyDescription("arma", headwords=("arma",)),),
        )
        corrected = TextUnit(
            "lesson-1",
            "Arma bona.",
            (VocabularyDescription("bona", headwords=("bonus",)),),
        )
        greek = TextUnit(
            "lesson-1",
            "Bona verba.",
            (VocabularyDescription("verba", headwords=("verbum",)),),
        )
        storage.upsert_text_unit(str(latin_deck_id), initial)
        storage.upsert_text_unit(str(latin_deck_id), corrected)
        storage.upsert_text_unit(str(greek_deck_id), greek)

        assert storage.list_text_units(str(latin_deck_id)) == (corrected,)
        assert storage.list_text_units(str(greek_deck_id)) == (greek,)

        note_type = collection.models.by_name(STORAGE_NOTE_TYPE_NAME)
        assert note_type is not None
        assert collection.models.field_names(note_type) == [
            "TextIdentifier",
            "Text",
            "VocabularyEntries",
        ]
        assert note_type["sortf"] == 0

        note_rows = db.all(
            """
            select notes.id, cards.id, cards.did, cards.queue
            from notes join cards on cards.nid = notes.id
            where notes.mid = ?
            order by notes.id
            """,
            note_type["id"],
        )
        assert len(note_rows) == 2
        assert {row[2] for row in note_rows} == {latin_deck_id, greek_deck_id}
        assert all(row[3] == -1 for row in note_rows)

        latin_note_id = db.scalar(
            "select id from notes where mid = ? and id in (select nid from cards where did = ?)",
            note_type["id"],
            latin_deck_id,
        )
        note = collection.get_note(NoteId(latin_note_id))
        assert note["TextIdentifier"] == "lesson-1"
        assert note["Text"] == "Arma bona."
        assert note["VocabularyEntries"] == '[{"surfaceForm": "bona", "headwords": ["bonus"]}]'
        assert collection.get_card(note_rows[0][1]).queue == -1

        storage.set_sentence_position(str(latin_deck_id), "lesson-1", 2)
        assert storage.get_sentence_position(str(latin_deck_id), "lesson-1") == 2
        reimported = TextUnit(
            "lesson-1",
            "Arma iterum.",
            (VocabularyDescription("iterum", headwords=("iterum",)),),
        )
        storage.upsert_text_unit(str(latin_deck_id), reimported)
        assert storage.get_sentence_position(str(latin_deck_id), "lesson-1") == 2
        reloaded_storage = AnkiTextUnitStorage(collection)
        assert reloaded_storage.get_sentence_position(str(latin_deck_id), "lesson-1") == 2
    finally:
        collection.close()
