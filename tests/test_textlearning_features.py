import ast
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from danki.textunit import TextLearning, TextUnit

scenarios("../docs/features/textlearning/")


@dataclass
class TextUnitState:
    current_text_unit: TextUnit | None = None
    selected_deck_id: str | None = None
    import_results: list[tuple[TextUnit | None, str | None]] = field(default_factory=list)
    reading_results: list[tuple[Any | None, str | None]] = field(default_factory=list)


@dataclass
class TextUnitFileSystem:
    documents: dict[str, str] = field(default_factory=dict)

    def write_document(self, name: str, content: str) -> None:
        self.documents[name] = content

    def read_document(self, name: str) -> str:
        try:
            return self.documents[name]
        except KeyError:
            pytest.fail(f"No text-unit JSON document named {name!r} exists.")


@pytest.fixture
def text_unit_state() -> TextUnitState:
    return TextUnitState()


@pytest.fixture
def text_unit_file_system() -> TextUnitFileSystem:
    return TextUnitFileSystem()


class InMemoryTextUnitStorage:
    def __init__(self) -> None:
        self.text_units: dict[tuple[str, str], TextUnit] = {}
        self.sentence_positions: dict[tuple[str, str], int] = {}

    def list_text_units(self, deck_id: str) -> tuple[TextUnit, ...]:
        return tuple(
            unit for (stored_deck_id, _), unit in self.text_units.items() if stored_deck_id == deck_id
        )

    def upsert_text_unit(self, deck_id: str, text_unit: TextUnit) -> None:
        self.text_units[(deck_id, text_unit.text_identifier)] = text_unit

    def get_sentence_position(self, deck_id: str, text_identifier: str) -> int:
        return self.sentence_positions.get((deck_id, text_identifier), 0)

    def set_sentence_position(self, deck_id: str, text_identifier: str, position: int) -> None:
        self.sentence_positions[(deck_id, text_identifier)] = position


@pytest.fixture
def text_unit_storage() -> InMemoryTextUnitStorage:
    return InMemoryTextUnitStorage()


@given("a fresh text-learning service", target_fixture="text_learning")
def fresh_text_learning(text_unit_storage: InMemoryTextUnitStorage) -> TextLearning:
    return TextLearning(text_unit_storage, text_unit_storage)


@given(parsers.parse('the pupil has selected deck "{deck_id}"'))
def pupil_has_selected_deck(deck_id: str, text_unit_state: TextUnitState) -> None:
    text_unit_state.selected_deck_id = deck_id


@given(parsers.parse("text unit {text_identifier} is stored with text:"))
def text_unit_is_stored(
    text_identifier: str,
    docstring: str,
    text_learning: TextLearning,
    text_unit_state: TextUnitState,
) -> None:
    text_unit = TextUnit(text_identifier, docstring, ())
    _store_text_unit(text_learning, _selected_deck_id(text_unit_state), text_unit)


@given(parsers.parse("text unit {text_identifier} is stored with empty text"))
def empty_text_unit_is_stored(
    text_identifier: str,
    text_learning: TextLearning,
    text_unit_state: TextUnitState,
) -> None:
    text_unit = TextUnit(text_identifier, "", ())
    _store_text_unit(text_learning, _selected_deck_id(text_unit_state), text_unit)


@given(parsers.parse("the saved sentence position for {text_identifier} is {position:d}"))
def saved_sentence_position(
    text_identifier: str,
    position: int,
    text_learning: TextLearning,
    text_unit_state: TextUnitState,
) -> None:
    deck_id = _selected_deck_id(text_unit_state)
    reading, error = text_learning.open_text_unit(deck_id, text_identifier)
    assert error is None
    assert reading is not None
    for _ in range(position):
        reading, error = text_learning.next_sentence(deck_id, text_identifier)
        assert error is None
        assert reading is not None


@when(parsers.parse("the pupil opens text unit {text_identifier}"))
def pupil_opens_text_unit(
    text_identifier: str,
    text_learning: TextLearning,
    text_unit_state: TextUnitState,
) -> None:
    result = text_learning.open_text_unit(_selected_deck_id(text_unit_state), text_identifier)
    text_unit_state.reading_results.append(result)


@when("the pupil moves to the next sentence")
def pupil_moves_to_next_sentence(text_learning: TextLearning, text_unit_state: TextUnitState) -> None:
    reading = _current_reading(text_unit_state)
    result = text_learning.next_sentence(_selected_deck_id(text_unit_state), reading.text_identifier)
    text_unit_state.reading_results.append(result)


@when("the pupil moves to the previous sentence")
def pupil_moves_to_previous_sentence(text_learning: TextLearning, text_unit_state: TextUnitState) -> None:
    reading = _current_reading(text_unit_state)
    result = text_learning.previous_sentence(_selected_deck_id(text_unit_state), reading.text_identifier)
    text_unit_state.reading_results.append(result)


@when("the pupil restarts the text")
def pupil_restarts_text(text_learning: TextLearning, text_unit_state: TextUnitState) -> None:
    reading = _current_reading(text_unit_state)
    result = text_learning.restart_text(_selected_deck_id(text_unit_state), reading.text_identifier)
    text_unit_state.reading_results.append(result)


@when(parsers.parse("the pupil reopens text unit {text_identifier}"))
def pupil_reopens_text_unit(
    text_identifier: str,
    text_learning: TextLearning,
    text_unit_state: TextUnitState,
) -> None:
    result = text_learning.open_text_unit(_selected_deck_id(text_unit_state), text_identifier)
    text_unit_state.reading_results.append(result)


@when(parsers.parse("the pupil updates text unit {text_identifier} with text:"))
def pupil_updates_text_unit(
    text_identifier: str,
    docstring: str,
    text_learning: TextLearning,
    text_unit_state: TextUnitState,
) -> None:
    current_units, error = text_learning.list_text_units(_selected_deck_id(text_unit_state))
    assert error is None
    assert current_units is not None
    current = next(unit for unit in current_units if unit.text_identifier == text_identifier)
    updated = TextUnit(current.text_identifier, docstring, current.vocabulary_entries)
    _store_text_unit(text_learning, _selected_deck_id(text_unit_state), updated)


@then(parsers.parse('the current sentence is "{sentence}"'))
def current_sentence_is(sentence: str, text_unit_state: TextUnitState) -> None:
    assert _current_reading(text_unit_state).current_sentence == sentence


@then("the current sentence is empty")
def current_sentence_is_empty(text_unit_state: TextUnitState) -> None:
    assert _current_reading(text_unit_state).current_sentence == ""


@then("the sentences are:")
def sentences_are(datatable: list[list[str]], text_unit_state: TextUnitState) -> None:
    assert _current_reading(text_unit_state).sentences == tuple(row[0] for row in datatable[1:])


@given(parsers.parse("the text-unit JSON document {document_name}:"))
def text_unit_json_document(
    document_name: str, docstring: str, text_unit_file_system: TextUnitFileSystem
) -> None:
    text_unit_file_system.write_document(document_name, docstring)


@given(parsers.parse('the document {document_name} is already stored in deck "{deck_id}"'))
def existing_text_unit_document_in_deck(
    document_name: str,
    deck_id: str,
    text_learning: TextLearning,
    text_unit_file_system: TextUnitFileSystem,
) -> None:
    document = text_unit_file_system.read_document(document_name)
    imported_text_unit, error = text_learning.import_text_unit(deck_id, document)
    if imported_text_unit is None or error is not None:
        pytest.fail(error or "The setup text unit could not be imported.")


@when(parsers.parse("the pupil imports the document {document_name}"))
def import_text_unit_document(
    document_name: str,
    text_learning: TextLearning,
    text_unit_file_system: TextUnitFileSystem,
    text_unit_state: TextUnitState,
) -> None:
    document = text_unit_file_system.read_document(document_name)
    result = text_learning.import_text_unit(_selected_deck_id(text_unit_state), document)
    text_unit_state.import_results.append(result)
    text_unit_state.current_text_unit = result[0]


@when(parsers.parse("the pupil exports the current text unit as document {document_name}"))
def export_text_unit(
    document_name: str, text_unit_state: TextUnitState, text_unit_file_system: TextUnitFileSystem
) -> None:
    text_unit = text_unit_state.current_text_unit
    assert text_unit is not None
    text_unit_file_system.write_document(document_name, TextLearning.export_text_unit(text_unit))


@when("the pupil views its text units", target_fixture="list_result")
def pupil_lists_text_units(text_learning: TextLearning, text_unit_state: TextUnitState):
    return text_learning.list_text_units(_selected_deck_id(text_unit_state))


@then(parsers.parse("document {actual_name} matches document {expected_name}"))
def exported_document_matches_source(
    actual_name: str, expected_name: str, text_unit_file_system: TextUnitFileSystem
) -> None:
    actual = text_unit_file_system.read_document(actual_name)
    expected = text_unit_file_system.read_document(expected_name)
    assert json.loads(actual) == json.loads(expected)


@then(parsers.parse('deck "{deck_id}" contains no text units'))
def deck_contains_no_text_units(text_learning: TextLearning, deck_id: str) -> None:
    text_units, error = text_learning.list_text_units(deck_id)
    assert error is None
    assert text_units == ()


@then(parsers.parse('deck "{deck_id}" contains exactly these text units:'))
def deck_contains_exactly_named_text_units(
    deck_id: str,
    datatable: list[list[str]],
    text_learning: TextLearning,
    text_unit_file_system: TextUnitFileSystem,
) -> None:
    text_units, error = text_learning.list_text_units(deck_id)
    assert error is None
    assert text_units is not None

    expected_documents = [
        json.dumps(
            json.loads(text_unit_file_system.read_document(row[0])),
            ensure_ascii=False,
            sort_keys=True,
        )
        for row in datatable
    ]
    actual_documents = [
        json.dumps(
            json.loads(TextLearning.export_text_unit(text_unit)),
            ensure_ascii=False,
            sort_keys=True,
        )
        for text_unit in text_units
    ]
    assert sorted(actual_documents) == sorted(expected_documents)


@then("the last import succeeds")
def last_import_succeeds(text_unit_state: TextUnitState) -> None:
    assert text_unit_state.import_results
    imported_text_unit, error = text_unit_state.import_results[-1]
    assert imported_text_unit is not None
    assert error is None


@then("the last import returns an error")
def last_import_returns_error(text_unit_state: TextUnitState) -> None:
    assert text_unit_state.import_results
    imported_text_unit, error = text_unit_state.import_results[-1]
    assert imported_text_unit is None
    assert error is not None


def _selected_deck_id(text_unit_state: TextUnitState) -> str:
    if text_unit_state.selected_deck_id is None:
        pytest.fail("The scenario must select a deck before a text-unit action.")
    return text_unit_state.selected_deck_id


def _store_text_unit(text_learning: TextLearning, deck_id: str, text_unit: TextUnit) -> None:
    _, error = text_learning.import_text_unit(deck_id, TextLearning.export_text_unit(text_unit))
    assert error is None


def _current_reading(text_unit_state: TextUnitState) -> Any:
    reading, error = text_unit_state.reading_results[-1]
    assert reading is not None
    assert error is None
    return reading


def test_text_learning_core_does_not_import_anki_or_qt() -> None:
    module_path = Path(__file__).parents[1] / "src" / "danki" / "textunit.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    forbidden_modules = {"anki", "aqt", "PyQt5", "PyQt6", "PySide2", "PySide6"}
    imports: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])

    assert imports.isdisjoint(forbidden_modules)
