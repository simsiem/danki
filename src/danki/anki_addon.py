"""Anki Desktop entry and thin Qt workflow for in-text help."""

from collections.abc import Callable
from importlib import import_module
from pathlib import Path
from typing import Any

from danki.anki_storage import AnkiTextUnitStorage, AnkiTextUnitStorageError
from danki.textunit import SentenceReading, TextLearning, TextUnit


def initialize() -> None:
    aqt = import_module("aqt")
    aqt.gui_hooks.main_window_did_init.append(lambda: _register_menu_action(aqt.mw))


def _register_menu_action(main_window: Any) -> None:
    qt = import_module("aqt.qt")
    action = qt.QAction("In-text help", main_window)
    action.triggered.connect(lambda _checked=False: _start_workflow(main_window))
    main_window.form.menuTools.addAction(action)


def _start_workflow(main_window: Any) -> None:
    qt = import_module("aqt.qt")
    decks = main_window.col.decks.all_names_and_ids()
    if not decks:
        qt.QMessageBox.information(main_window, "In-text help", "No decks are available.")
        return

    deck_names = [deck.name for deck in decks]
    selected_name, accepted = qt.QInputDialog.getItem(
        main_window, "In-text help", "Deck", deck_names, 0, False
    )
    if not accepted:
        return
    selected_deck = next(deck for deck in decks if deck.name == selected_name)
    deck_id = str(selected_deck.id)
    storage = AnkiTextUnitStorage(main_window.col)
    learning = TextLearning(storage, storage)
    _show_text_units(main_window, learning, deck_id)


def _show_text_units(main_window: Any, learning: TextLearning, deck_id: str) -> None:
    qt = import_module("aqt.qt")
    dialog = qt.QDialog(main_window)
    dialog.setWindowTitle("In-text help")
    layout = qt.QVBoxLayout(dialog)
    text_list = qt.QListWidget(dialog)
    empty_state = qt.QLabel("No text units are stored in this deck.", dialog)
    buttons = qt.QHBoxLayout()
    open_button = qt.QPushButton("Open", dialog)
    import_button = qt.QPushButton("Import JSON", dialog)
    close_button = qt.QPushButton("Close", dialog)
    layout.addWidget(empty_state)
    layout.addWidget(text_list)
    buttons.addWidget(open_button)
    buttons.addWidget(import_button)
    buttons.addWidget(close_button)
    layout.addLayout(buttons)

    text_units: list[TextUnit] = []
    selected_identifier: str | None = None

    def refresh_text_units() -> None:
        text_list.clear()
        units, error = learning.list_text_units(deck_id)
        if error is not None or units is None:
            qt.QMessageBox.warning(dialog, "In-text help", error or "Text units could not be loaded.")
            text_units.clear()
        else:
            text_units[:] = units
            for text_unit in text_units:
                text_list.addItem(text_unit.text_identifier)
        is_empty = not text_units
        empty_state.setVisible(is_empty)
        text_list.setVisible(not is_empty)
        open_button.setEnabled(not is_empty)

    def import_text_unit() -> None:
        file_path, _file_filter = qt.QFileDialog.getOpenFileName(
            dialog, "Import text unit", "", "JSON files (*.json)"
        )
        if not file_path:
            return
        try:
            document = Path(file_path).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as file_error:
            qt.QMessageBox.warning(dialog, "In-text help", f"The file could not be read: {file_error}")
            return
        text_unit, error = _import_text_unit(learning, deck_id, document)
        if error is not None or text_unit is None:
            qt.QMessageBox.warning(dialog, "In-text help", error or "The text unit could not be imported.")
            return
        refresh_text_units()

    def open_text_unit() -> None:
        nonlocal selected_identifier
        row = text_list.currentRow()
        if row < 0:
            return
        selected_identifier = text_units[row].text_identifier
        dialog.accept()

    import_button.clicked.connect(import_text_unit)
    open_button.clicked.connect(open_text_unit)
    close_button.clicked.connect(dialog.reject)
    text_list.itemDoubleClicked.connect(open_text_unit)
    refresh_text_units()
    dialog.exec()

    if selected_identifier is None:
        return
    reading, error = learning.open_text_unit(deck_id, selected_identifier)
    if error is not None or reading is None:
        qt.QMessageBox.warning(main_window, "In-text help", error or "The text unit could not be opened.")
        return
    _show_sentence(main_window, learning, deck_id, reading)


def _import_text_unit(
    learning: TextLearning, deck_id: str, document: str
) -> tuple[TextUnit | None, str | None]:
    try:
        return learning.import_text_unit(deck_id, document)
    except AnkiTextUnitStorageError as error:
        return None, str(error)


def _show_sentence(
    main_window: Any,
    learning: TextLearning,
    deck_id: str,
    reading: SentenceReading,
) -> None:
    qt = import_module("aqt.qt")
    dialog = qt.QDialog(main_window)
    dialog.setWindowTitle("In-text help")
    layout = qt.QVBoxLayout(dialog)
    sentence_label = qt.QLabel(dialog)
    sentence_label.setWordWrap(True)
    buttons = qt.QHBoxLayout()
    previous_button = qt.QPushButton("Previous", dialog)
    restart_button = qt.QPushButton("Restart", dialog)
    next_button = qt.QPushButton("Next", dialog)
    close_button = qt.QPushButton("Close", dialog)
    for button in (previous_button, restart_button, next_button, close_button):
        buttons.addWidget(button)
    layout.addWidget(sentence_label)
    layout.addLayout(buttons)

    current_reading = reading

    def display_reading() -> None:
        sentence_label.setText(current_reading.current_sentence)
        previous_button.setEnabled(current_reading.sentence_index > 0)
        next_button.setEnabled(current_reading.sentence_index + 1 < len(current_reading.sentences))

    def apply_navigation(operation: Callable[[str, str], tuple[SentenceReading | None, str | None]]) -> None:
        nonlocal current_reading
        updated_reading, error = operation(deck_id, current_reading.text_identifier)
        if error is not None or updated_reading is None:
            qt.QMessageBox.warning(dialog, "In-text help", error or "The sentence could not be changed.")
            return
        current_reading = updated_reading
        display_reading()

    previous_button.clicked.connect(lambda: apply_navigation(learning.previous_sentence))
    restart_button.clicked.connect(lambda: apply_navigation(learning.restart_text))
    next_button.clicked.connect(lambda: apply_navigation(learning.next_sentence))
    close_button.clicked.connect(dialog.accept)
    display_reading()
    dialog.exec()
