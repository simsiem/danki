"""Installed-bundle smoke journey; run only in the dedicated Hatch UI environment."""

import sys
from collections.abc import Iterator
from importlib import import_module
from pathlib import Path
from time import monotonic

import pytest
from aqt.main import AnkiQt  # pyrefly: ignore[missing-import]
from aqt.qt import (  # pyrefly: ignore[missing-import]
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QEvent,
    QLabel,
    QListWidget,
    QPushButton,
    Qt,
    QTimer,
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


def _dialog() -> QDialog:
    dialog = QApplication.activeModalWidget()
    assert isinstance(dialog, QDialog), "Expected an active Qt dialog."
    assert dialog.windowTitle() == "In-text help", dialog.windowTitle()
    return dialog


def _button(dialog: QDialog, text: str) -> QPushButton:
    matches = [button for button in dialog.findChildren(QPushButton) if button.text() == text]
    assert len(matches) == 1, f"Expected one {text!r} button."
    return matches[0]


@given("the standalone add-on is installed in an isolated Anki Desktop profile")
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


def _read_text(desktop, qtbot, identifier: str, deck: str, *, advance: bool) -> list[str]:
    action = next(a for a in desktop.mw.form.menuTools.actions() if a.text() == "In-text help")
    sentences: list[str] = []
    errors: list[AssertionError] = []
    stage = 0
    deadline = monotonic() + TIMEOUT_MS / 1000
    timer = QTimer()
    timer.setInterval(10)

    def cancel() -> None:
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QDialog) and widget.isVisible():
                widget.reject()

    def drive() -> None:
        nonlocal stage
        try:
            assert monotonic() < deadline, f"Timed out at UI stage {stage}."
            if QApplication.activeModalWidget() is None:
                return
            dialog = _dialog()
            if stage == 0:
                combo = dialog.findChild(QComboBox)
                assert combo is not None, "Expected the deck picker."
                index = combo.findText(deck)
                assert index >= 0
                combo.setFocus()
                qtbot.keyClick(combo, Qt.Key.Key_Home)
                for _ in range(index):
                    qtbot.keyClick(combo, Qt.Key.Key_Down)
                assert combo.currentText() == deck
                buttons = dialog.findChild(QDialogButtonBox)
                assert buttons is not None
                ok = buttons.button(QDialogButtonBox.StandardButton.Ok)
                assert ok is not None
                stage = 1
                qtbot.mouseClick(ok, Qt.MouseButton.LeftButton)
            elif stage == 1:
                texts = dialog.findChild(QListWidget)
                assert texts is not None, "Expected the text-unit list."
                assert texts.count() == 1
                assert texts.item(0).text() == identifier
                texts.setFocus()
                qtbot.keyClick(texts, Qt.Key.Key_Home)
                assert texts.currentRow() == 0
                stage = 2
                qtbot.mouseClick(_button(dialog, "Open"), Qt.MouseButton.LeftButton)
            else:
                labels = [label for label in dialog.findChildren(QLabel) if label.isVisible()]
                assert len(labels) == 1
                sentences.append(labels[0].text())
                if stage == 2 and advance:
                    next_button = _button(dialog, "Next")
                    assert next_button.isEnabled()
                    stage = 3
                    qtbot.mouseClick(next_button, Qt.MouseButton.LeftButton)
                else:
                    stage = 4
                    timer.stop()
                    qtbot.mouseClick(_button(dialog, "Close"), Qt.MouseButton.LeftButton)
        except AssertionError as error:
            # Assertions in timer callbacks must unwind modal loops and fail the test.
            errors.append(error)
            timer.stop()
            cancel()

    timer.timeout.connect(drive)
    timer.start()
    try:
        action.trigger()
    finally:
        timer.stop()
        cancel()
    if errors:
        raise errors[0]
    assert stage == 4, f"The menu workflow returned before reading finished (stage {stage})."
    qtbot.waitUntil(lambda: QApplication.activeModalWidget() is None, timeout=TIMEOUT_MS)
    return sentences


@when(
    parsers.parse(
        'the pupil opens "{identifier}" in deck "{deck}", advances a sentence, closes it, and reopens it'
    ),
    target_fixture="observed_sentences",
)
def read_and_reopen(desktop, qtbot, identifier: str, deck: str) -> list[str]:
    first_visit = _read_text(desktop, qtbot, identifier, deck, advance=True)
    second_visit = _read_text(desktop, qtbot, identifier, deck, advance=False)
    return first_visit + second_visit


@then(parsers.parse('the initial reading dialog displayed "{sentence}"'))
def initial_sentence(observed_sentences: list[str], sentence: str) -> None:
    assert len(observed_sentences) == 3
    assert observed_sentences[0] == sentence


@then(parsers.parse('navigation displayed "{sentence}"'))
def navigated_sentence(observed_sentences: list[str], sentence: str) -> None:
    assert observed_sentences[1] == sentence


@then(parsers.parse('the reopened reading dialog displayed "{sentence}"'))
def reopened_sentence(observed_sentences: list[str], sentence: str) -> None:
    assert observed_sentences[2] == sentence
