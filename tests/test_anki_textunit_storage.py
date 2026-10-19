import pytest
from anki.collection import Collection
from anki.notes import NoteId

from danki.anki_storage import STORAGE_NOTE_TYPE_NAME, AnkiTextUnitStorage
from danki.textunit import TextLearning, TextUnit, VocabularyDescription


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


def test_vocabulary_lookup_is_exact_and_prefers_nearest_deck(tmp_path) -> None:
    collection = Collection(str(tmp_path / "collection.anki2"))
    try:
        storage = AnkiTextUnitStorage(collection)
        parent_id = collection.decks.id("Latin")
        child_id = collection.decks.id("Latin::Class")
        assert parent_id is not None
        assert child_id is not None

        note_type = collection.models.new("Danki Lookup Vocabulary")
        collection.models.add_field(note_type, collection.models.new_field("Headword"))
        collection.models.add_field(note_type, collection.models.new_field("Meaning"))
        template = collection.models.new_template("Card")
        template["qfmt"] = "{{Headword}}"
        template["afmt"] = "{{FrontSide}}<hr>{{Meaning}}"
        collection.models.add_template(note_type, template)
        note_type["sortf"] = 0
        collection.models.add_dict(note_type)
        note_type = collection.models.by_name("Danki Lookup Vocabulary")
        assert note_type is not None

        def add_entry(deck_id: int, headword: str, meaning: str) -> None:
            note = collection.new_note(note_type)
            note["Headword"] = headword
            note["Meaning"] = meaning
            collection.add_note(note, deck_id)

        add_entry(parent_id, "amo", "parent meaning")
        add_entry(child_id, "amo", "nearest meaning")
        add_entry(child_id, "Sol", "the sun")

        learning = TextLearning(storage, storage, storage)
        resolved, error = learning.resolve_headword(str(child_id), "amo")
        assert error is None
        assert resolved is not None
        assert resolved.deck_id == str(child_id)
        assert dict(resolved.fields)["Meaning"] == "nearest meaning"

        unresolved, error = learning.resolve_headword(str(child_id), "sol")
        assert unresolved is None
        assert error == "No vocabulary note for headword 'sol' was found in this deck or its parent decks."

        add_entry(child_id, "amo", "duplicate meaning")
        duplicate, error = learning.resolve_headword(str(child_id), "amo")
        assert duplicate is None
        assert error == (
            f"Headword 'amo' matches multiple vocabulary notes in deck '{collection.decks.name(child_id)}'."
        )
    finally:
        collection.close()
