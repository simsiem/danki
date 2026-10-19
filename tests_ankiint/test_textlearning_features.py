"""Installed-bundle smoke journey; run only in the dedicated Hatch UI environment."""

import sys
from collections.abc import Iterator
from importlib import import_module
from pathlib import Path

import pytest
from aqt.main import AnkiQt  # pyrefly: ignore[missing-import]
from aqt.qt import (  # pyrefly: ignore[missing-import]
    QApplication,
    QDialog,
    QEvent,
    QLabel,
    QPoint,
    QPushButton,
    Qt,
    QTextBrowser,
    QTreeWidget,
    QWidget,
)
from pytest_anki._plugin import patch  # pyrefly: ignore[missing-import]
from pytest_anki._plugin.launch import anki_running  # pyrefly: ignore[missing-import]
from pytest_bdd import given, parsers, scenarios, then, when

from scripts.build_anki_addon import build_anki_addon

scenarios("../docs/features/textlearning_ankiint/")

TIMEOUT_MS = 10000


@pytest.fixture
def desktop(tmp_path, monkeypatch, qtbot) -> Iterator:
    # pytest-anki2's replacement initializer omits main_window_did_init on Anki 26.9.3.
    # Keep its isolated session management, but run Anki's actual initializer and loader.
    original_init = AnkiQt.__init__
    original_setup_addons = AnkiQt.setupAddons

    def setup_addons(main_window, args) -> None:
        destination = Path(main_window.pm.addonFolder()) / "danki_in_text_help"
        build_anki_addon(destination)
        original_setup_addons(main_window, args)

    monkeypatch.setattr(patch, "custom_init_factory", lambda **_kwargs: original_init)
    monkeypatch.setattr(AnkiQt, "setupAddons", setup_addons)
    assert not any(name == "danki" or name.startswith("danki.") for name in sys.modules), (
        "The UI suite must not preload source-tree Danki modules."
    )
    manager = anki_running(qtbot=qtbot, base_path=str(tmp_path))
    session = manager.__enter__()
    base = Path(session.base)
    try:
        qtbot.waitUntil(lambda: session.mw.col is not None, timeout=TIMEOUT_MS)
        qtbot.waitUntil(
            lambda: any(a.text() == "In-text help" for a in session.mw.form.menuTools.actions()),
            timeout=TIMEOUT_MS,
        )
        installed = base / "addons21" / "danki_in_text_help"
        for name in ("danki", "danki.anki_addon", "danki.anki_storage", "danki.textunit"):
            module = import_module(name)
            assert module.__file__ is not None
            assert Path(module.__file__).resolve().is_relative_to(installed.resolve()), name
        yield session
    finally:
        try:
            for widget in QApplication.topLevelWidgets():
                if isinstance(widget, QDialog) and widget.isVisible():
                    widget.reject()
            if session.mw.col is not None:
                session.unload_profile()
                qtbot.waitUntil(lambda: session.mw.col is None, timeout=TIMEOUT_MS)
            session.mw.backend.await_backup_completion()
        finally:
            # The upstream context manager skips teardown if an exception crosses its yield.
            # Exit it normally even when a scenario assertion failed; that assertion still propagates.
            manager.__exit__(None, None, None)
            QApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
            assert not base.exists(), "The isolated Anki base directory was not removed."


def _button(parent: QWidget, text: str) -> QPushButton:
    matches = [button for button in parent.findChildren(QPushButton) if button.text() == text]
    assert len(matches) == 1, f"Expected one {text!r} button."
    return matches[0]


def _visible_view(main_window, child_name: str) -> QWidget | None:
    return next(
        (
            page
            for page in main_window.findChildren(QWidget, "dankiInTextHelpView")
            if page.isVisible() and page.findChild(QWidget, child_name) is not None
        ),
        None,
    )


def _text_tree(main_window) -> QTreeWidget:
    view = _visible_view(main_window, "dankiDeckTextTree")
    assert view is not None, "The in-text help decks view is not visible."
    tree = view.findChild(QTreeWidget, "dankiDeckTextTree")
    assert tree is not None
    return tree


@given("the Danki add-on is installed in an isolated Anki Desktop profile")
def installed_addon(desktop) -> None:
    assert desktop.collection is not None


@given(parsers.parse('deck "{deck}" contains text unit "{identifier}" with text "{text}"'))
def seed_text(desktop, deck: str, identifier: str, text: str) -> None:
    storage_module = import_module("danki.anki_storage")
    core = import_module("danki.textunit")
    deck_id = desktop.collection.decks.id(deck)
    assert deck_id is not None
    storage = storage_module.AnkiTextUnitStorage(desktop.collection)
    learning = core.TextLearning(storage, storage)
    unit = core.TextUnit(identifier, text, ())
    imported, error = learning.import_text_unit(str(deck_id), learning.export_text_unit(unit))
    assert error is None, error
    assert imported == unit


@given(parsers.parse('deck "{deck}" contains text unit "{identifier}" with described forms'))
def seed_described_text(desktop, deck: str, identifier: str, datatable: list[list[str]]) -> None:
    storage_module = import_module("danki.anki_storage")
    core = import_module("danki.textunit")
    deck_id = desktop.collection.decks.id(deck)
    assert deck_id is not None
    descriptions = tuple(
        core.VocabularyDescription(
            row[0],
            headwords=tuple(value.strip() for value in row[1].split(",")) if row[1] else None,
            notes=row[2] or None,
        )
        for row in datatable[1:]
    )
    storage = storage_module.AnkiTextUnitStorage(desktop.collection)
    learning = core.TextLearning(storage, storage, storage)
    unit = core.TextUnit(identifier, " ".join(row[0] for row in datatable[1:]) + ".", descriptions)
    imported, error = learning.import_text_unit(str(deck_id), learning.export_text_unit(unit))
    assert error is None, error
    assert imported == unit


@given(parsers.parse('vocabulary note "{headword}" exists in deck "{deck}" with meaning "{meaning}"'))
def seed_vocabulary_note(desktop, deck: str, headword: str, meaning: str) -> None:
    collection = desktop.collection
    deck_id = collection.decks.id(deck)
    assert deck_id is not None
    note_type = collection.models.by_name("Danki Ticket 03 Vocabulary")
    if note_type is None:
        note_type = collection.models.new("Danki Ticket 03 Vocabulary")
        collection.models.add_field(note_type, collection.models.new_field("Headword"))
        collection.models.add_field(note_type, collection.models.new_field("Meaning"))
        template = collection.models.new_template("Vocabulary")
        template["qfmt"] = "{{Headword}}"
        template["afmt"] = "{{FrontSide}}<hr>{{Meaning}}"
        collection.models.add_template(note_type, template)
        note_type["sortf"] = 0
        collection.models.add_dict(note_type)
        note_type = collection.models.by_name("Danki Ticket 03 Vocabulary")
    assert note_type is not None
    note = collection.new_note(note_type)
    note["Headword"] = headword
    note["Meaning"] = meaning
    collection.add_note(note, deck_id)


@when("the pupil activates in-text help")
def activate_in_text_help(desktop) -> None:
    action = next(a for a in desktop.mw.form.menuTools.actions() if a.text() == "In-text help")
    action.trigger()


@then("Anki shows the in-text help decks view")
def decks_view_is_visible(desktop, qtbot) -> None:
    qtbot.waitUntil(
        lambda: _visible_view(desktop.mw, "dankiDeckTextTree") is not None,
        timeout=TIMEOUT_MS,
    )


@when(parsers.parse('the pupil expands deck "{deck}"'))
def expand_deck(desktop, qtbot, deck: str) -> None:
    tree = _text_tree(desktop.mw)
    deck_item = next(
        tree.topLevelItem(index)
        for index in range(tree.topLevelItemCount())
        if tree.topLevelItem(index).text(0) == deck
    )
    deck_item.setExpanded(True)
    qtbot.waitUntil(lambda: deck_item.childCount() == 1, timeout=TIMEOUT_MS)


@then(parsers.parse('Anki shows text unit "{identifier}" in deck "{deck}"'))
def text_unit_is_shown(desktop, identifier: str, deck: str) -> None:
    tree = _text_tree(desktop.mw)
    deck_item = next(
        tree.topLevelItem(index)
        for index in range(tree.topLevelItemCount())
        if tree.topLevelItem(index).text(0) == deck
    )
    assert deck_item.isExpanded()
    assert any(deck_item.child(index).text(0) == identifier for index in range(deck_item.childCount()))


@when(parsers.parse('the pupil opens text unit "{identifier}" in deck "{deck}"'))
def open_text_unit(desktop, qtbot, identifier: str, deck: str) -> None:
    tree = _text_tree(desktop.mw)
    deck_item = next(
        tree.topLevelItem(index)
        for index in range(tree.topLevelItemCount())
        if tree.topLevelItem(index).text(0) == deck
    )
    text_item = next(
        deck_item.child(index)
        for index in range(deck_item.childCount())
        if deck_item.child(index).text(0) == identifier
    )
    tree.setCurrentItem(text_item)
    view = _visible_view(desktop.mw, "dankiDeckTextTree")
    assert view is not None
    qtbot.mouseClick(_button(view, "Open"), Qt.MouseButton.LeftButton)


@then(parsers.parse('Anki shows the sentence view with the sentence "{sentence}"'))
def sentence_view_shows_sentence(desktop, qtbot, sentence: str) -> None:
    qtbot.waitUntil(
        lambda: _visible_view(desktop.mw, "dankiCurrentSentence") is not None,
        timeout=TIMEOUT_MS,
    )
    sentence_view = _visible_view(desktop.mw, "dankiCurrentSentence")
    assert sentence_view is not None
    sentence_browser = sentence_view.findChild(QTextBrowser, "dankiCurrentSentence")
    assert sentence_browser is not None
    assert sentence_browser.toPlainText() == sentence


@when(parsers.parse('the pupil clicks the described form "{surface_form}"'))
def click_described_form(desktop, qtbot, surface_form: str) -> None:
    view = _visible_view(desktop.mw, "dankiCurrentSentence")
    assert view is not None
    browser = view.findChild(QTextBrowser, "dankiCurrentSentence")
    assert browser is not None
    cursor = browser.document().find(surface_form)
    assert not cursor.isNull(), f"The described form {surface_form!r} is not rendered."
    expected_href = surface_form.casefold()
    position = next(
        (
            QPoint(x, y)
            for y in range(0, browser.viewport().height(), 2)
            for x in range(0, browser.viewport().width(), 2)
            if browser.anchorAt(QPoint(x, y)) == expected_href
        ),
        None,
    )
    assert position is not None, f"The described form {surface_form!r} has no clickable anchor."
    qtbot.mouseClick(browser.viewport(), Qt.MouseButton.LeftButton, pos=position)


@then(parsers.parse('Anki shows notes "{notes}"'))
def notes_are_visible(desktop, notes: str) -> None:
    view = _visible_view(desktop.mw, "dankiVocabularyCardArea")
    assert view is not None
    content = view.findChild(QLabel, "dankiCardContent")
    assert content is not None
    assert content.text() == notes


@then(parsers.parse('Anki shows candidate headwords "{headwords}"'))
def candidate_headwords_are_visible(desktop, headwords: str) -> None:
    view = _visible_view(desktop.mw, "dankiVocabularyCardArea")
    assert view is not None
    area = view.findChild(QWidget, "dankiVocabularyCardArea")
    assert area is not None
    actual = [button.text() for button in area.findChildren(QPushButton)]
    assert actual == [value.strip() for value in headwords.split(",")]


@when(parsers.parse('the pupil chooses candidate "{headword}"'))
def choose_candidate(desktop, qtbot, headword: str) -> None:
    view = _visible_view(desktop.mw, "dankiVocabularyCardArea")
    assert view is not None
    qtbot.mouseClick(_button(view, headword), Qt.MouseButton.LeftButton)


@then(parsers.parse('Anki shows the vocabulary entry for "{headword}" with meaning "{meaning}"'))
def vocabulary_entry_is_visible(desktop, headword: str, meaning: str) -> None:
    view = _visible_view(desktop.mw, "dankiVocabularyCardArea")
    assert view is not None
    content = view.findChild(QLabel, "dankiCardContent")
    assert content is not None
    assert content.text() == f"{headword}\nMeaning: {meaning}"


@then(parsers.parse('Anki shows the lookup error "{message}"'))
def lookup_error_is_visible(desktop, message: str) -> None:
    view = _visible_view(desktop.mw, "dankiVocabularyCardArea")
    assert view is not None
    content = view.findChild(QLabel, "dankiCardContent")
    assert content is not None
    assert content.text() == message


@when(parsers.parse('the pupil clicks the "{label}" button'))
def click_button(desktop, qtbot, label: str) -> None:
    view = _visible_view(desktop.mw, "dankiCurrentSentence")
    assert view is not None, "The sentence view is not visible."
    qtbot.mouseClick(_button(view, label), Qt.MouseButton.LeftButton)
