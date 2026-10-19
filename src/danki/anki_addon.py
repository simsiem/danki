"""Anki Desktop entry and thin Qt workflow for in-text help."""

from collections.abc import Callable
from html import escape
from importlib import import_module
from pathlib import Path
from typing import Any
from urllib.parse import quote, unquote

from danki.anki_storage import AnkiTextUnitStorage, AnkiTextUnitStorageError
from danki.textunit import SentenceReading, TextLearning, TextUnit


def initialize() -> None:
    aqt = import_module("aqt")
    aqt.gui_hooks.main_window_did_init.append(lambda: _register_menu_action(aqt.mw))


def _register_menu_action(main_window: Any) -> None:
    aqt = import_module("aqt")
    qt = import_module("aqt.qt")
    action = qt.QAction("In-text help", main_window)
    action.triggered.connect(lambda _checked=False: _start_workflow(main_window))
    main_window.form.menuTools.addAction(action)

    def restore_native_content(_new_state: str, _old_state: str) -> None:
        _restore_plugin_view(main_window)

    aqt.gui_hooks.state_will_change.append(restore_native_content)


def _restore_plugin_view(main_window: Any, keep_page: Any | None = None) -> None:
    qt = import_module("aqt.qt")
    pages = main_window.findChildren(qt.QWidget, "dankiInTextHelpView")
    for page in pages:
        if page is keep_page:
            continue
        main_window.mainLayout.replaceWidget(page, main_window.web)
        page.hide()
        page.deleteLater()


def _install_plugin_view(main_window: Any, page: Any) -> None:
    _restore_plugin_view(main_window, page)
    main_window.mainLayout.replaceWidget(main_window.web, page)
    main_window.web.hide()
    page.show()


def _start_workflow(main_window: Any) -> None:
    storage = AnkiTextUnitStorage(main_window.col)
    learning = TextLearning(storage, storage, storage)
    _show_text_units(main_window, learning)


def _show_text_units(
    main_window: Any,
    learning: TextLearning,
    expanded_deck_id: str | None = None,
) -> None:
    qt = import_module("aqt.qt")
    page = qt.QWidget(main_window.form.centralwidget)
    page.setObjectName("dankiInTextHelpView")
    layout = qt.QVBoxLayout(page)
    tree = qt.QTreeWidget(page)
    tree.setObjectName("dankiDeckTextTree")
    tree.setHeaderHidden(True)
    empty_state = qt.QLabel("No decks are available.", page)
    buttons = qt.QHBoxLayout()
    import_button = qt.QPushButton("Import JSON", page)
    open_button = qt.QPushButton("Open", page)
    layout.addWidget(empty_state)
    layout.addWidget(tree)
    buttons.addWidget(import_button)
    buttons.addWidget(open_button)
    layout.addLayout(buttons)

    user_role = qt.Qt.ItemDataRole.UserRole
    loaded_decks: set[str] = set()
    deck_items: dict[str, Any] = {}

    def load_text_units(deck_item: Any) -> None:
        item_data = deck_item.data(0, user_role)
        if not item_data or item_data[0] != "deck":
            return
        deck_id = item_data[1]
        if deck_id in loaded_decks:
            return
        loaded_decks.add(deck_id)
        while deck_item.childCount():
            deck_item.takeChild(0)
        units, error = learning.list_text_units(deck_id)
        if error is not None or units is None:
            qt.QMessageBox.warning(main_window, "In-text help", error or "Text units could not be loaded.")
            return
        if not units:
            empty_item = qt.QTreeWidgetItem(["No text units stored in this deck."])
            empty_item.setDisabled(True)
            deck_item.addChild(empty_item)
            return
        for text_unit in units:
            text_item = qt.QTreeWidgetItem([text_unit.text_identifier])
            text_item.setData(0, user_role, ("text", deck_id, text_unit.text_identifier))
            deck_item.addChild(text_item)

    def current_selection_changed(current: Any, _previous: Any) -> None:
        item_data = current.data(0, user_role) if current is not None else None
        open_button.setEnabled(bool(item_data and item_data[0] == "text"))
        import_button.setEnabled(bool(item_data and item_data[0] in {"deck", "text"}))

    def open_text_unit() -> None:
        item = tree.currentItem()
        item_data = item.data(0, user_role) if item is not None else None
        if not item_data or item_data[0] != "text":
            return
        _, deck_id, text_identifier = item_data
        reading, error = learning.open_text_unit(deck_id, text_identifier)
        if error is not None or reading is None:
            qt.QMessageBox.warning(main_window, "In-text help", error or "The text unit could not be opened.")
            return
        _show_sentence(main_window, learning, deck_id, reading)

    def import_text_unit() -> None:
        item = tree.currentItem()
        item_data = item.data(0, user_role) if item is not None else None
        if not item_data or item_data[0] not in {"deck", "text"}:
            return
        deck_id = item_data[1]
        file_path, _file_filter = qt.QFileDialog.getOpenFileName(
            main_window, "Import text unit", "", "JSON files (*.json)"
        )
        if not file_path:
            return
        try:
            document = Path(file_path).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as file_error:
            qt.QMessageBox.warning(main_window, "In-text help", f"The file could not be read: {file_error}")
            return
        text_unit, error = _import_text_unit(learning, deck_id, document)
        if error is not None or text_unit is None:
            qt.QMessageBox.warning(
                main_window, "In-text help", error or "The text unit could not be imported."
            )
            return
        deck_item = deck_items[deck_id]
        loaded_decks.discard(deck_id)
        load_text_units(deck_item)
        deck_item.setExpanded(True)

    tree.itemExpanded.connect(load_text_units)
    tree.currentItemChanged.connect(current_selection_changed)
    tree.itemDoubleClicked.connect(lambda _item, _column: open_text_unit())
    import_button.clicked.connect(import_text_unit)
    open_button.clicked.connect(open_text_unit)

    decks = main_window.col.decks.all_names_and_ids()
    empty_state.setVisible(not decks)
    tree.setVisible(bool(decks))
    for deck in decks:
        deck_id = str(deck.id)
        deck_item = qt.QTreeWidgetItem([deck.name])
        deck_item.setData(0, user_role, ("deck", deck_id))
        deck_item.addChild(qt.QTreeWidgetItem([""]))
        tree.addTopLevelItem(deck_item)
        deck_items[deck_id] = deck_item
        if deck_id == expanded_deck_id:
            deck_item.setExpanded(True)

    open_button.setEnabled(False)
    import_button.setEnabled(False)
    _install_plugin_view(main_window, page)


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
    page = qt.QWidget(main_window.form.centralwidget)
    page.setObjectName("dankiInTextHelpView")
    layout = qt.QVBoxLayout(page)
    back_button = qt.QPushButton("Back to decks", page)
    sentence_view = qt.QTextBrowser(page)
    sentence_view.setObjectName("dankiCurrentSentence")
    sentence_view.setOpenLinks(False)
    sentence_view.setOpenExternalLinks(False)
    sentence_view.setMaximumHeight(140)
    restart_button = qt.QPushButton("Restart", page)
    previous_button = qt.QPushButton("Previous", page)
    next_button = qt.QPushButton("Next", page)
    buttons = qt.QHBoxLayout()
    buttons.addStretch()
    button_width = back_button.sizeHint().width()
    for button in (back_button, restart_button, previous_button, next_button):
        button.setSizePolicy(qt.QSizePolicy.Policy.Maximum, qt.QSizePolicy.Policy.Fixed)
        button.setFixedWidth(button_width)
        buttons.addWidget(button)
    buttons.addStretch()
    card_area = qt.QFrame(page)
    card_area.setObjectName("dankiVocabularyCardArea")
    card_area.setFrameShape(qt.QFrame.Shape.StyledPanel)
    card_layout = qt.QVBoxLayout(card_area)
    card_content = qt.QLabel("", card_area)
    card_content.setObjectName("dankiCardContent")
    card_content.setWordWrap(True)
    card_layout.addWidget(card_content)
    layout.addWidget(sentence_view)
    layout.addLayout(buttons)
    layout.addWidget(card_area, 1)

    current_reading = reading

    def clear_card_area() -> None:
        for index in reversed(range(card_layout.count())):
            item = card_layout.itemAt(index)
            widget = item.widget()
            if widget is not None and widget is not card_content:
                card_layout.removeWidget(widget)
                widget.deleteLater()
        card_content.clear()

    def show_message(message: str) -> None:
        clear_card_area()
        card_content.setText(message)

    def select_surface_form(surface_form: str) -> None:
        help_description, error = learning.select_surface_form(
            deck_id, current_reading.text_identifier, current_reading.sentence_index, surface_form
        )
        if error is not None or help_description is None:
            show_message(error or "The selected surface form could not be opened.")
            return
        clear_card_area()
        if help_description.notes is not None:
            card_content.setText(help_description.notes)
            return
        if help_description.headwords is None:
            show_message("No help is available for this surface form.")
            return
        for headword in help_description.headwords:
            candidate_button = qt.QPushButton(headword, card_area)
            candidate_button.clicked.connect(lambda _checked=False, word=headword: show_candidate(word))
            card_layout.addWidget(candidate_button)

    def show_candidate(headword: str) -> None:
        vocabulary_entry, error = learning.resolve_headword(deck_id, headword)
        if error is not None or vocabulary_entry is None:
            show_message(error or f"No vocabulary note for headword '{headword}' was found.")
            return
        clear_card_area()
        field_lines = [headword]
        field_lines.extend(
            f"{field_name}: {value}"
            for field_name, value in vocabulary_entry.fields
            if field_name != "Headword" and value
        )
        card_content.setText("\n".join(field_lines))

    def render_sentence() -> None:
        occurrences, error = learning.surface_forms_for_sentence(
            deck_id, current_reading.text_identifier, current_reading.sentence_index
        )
        if error is not None or occurrences is None:
            sentence_view.setPlainText(current_reading.current_sentence)
            show_message(error or "Surface forms could not be loaded.")
            return
        sentence = current_reading.current_sentence
        links: list[str] = []
        cursor = 0
        for occurrence in occurrences:
            links.append(escape(sentence[cursor : occurrence.start]))
            surface_form = quote(occurrence.surface_form, safe="")
            links.append(f'<a href="{surface_form}"><b>{escape(occurrence.matched_text)}</b></a>')
            cursor = occurrence.end
        links.append(escape(sentence[cursor:]))
        sentence_view.setHtml("".join(links))

    def display_reading() -> None:
        render_sentence()
        previous_button.setEnabled(current_reading.sentence_index > 0)
        next_button.setEnabled(current_reading.sentence_index + 1 < len(current_reading.sentences))

    def apply_navigation(operation: Callable[[str, str], tuple[SentenceReading | None, str | None]]) -> None:
        nonlocal current_reading
        updated_reading, error = operation(deck_id, current_reading.text_identifier)
        if error is not None or updated_reading is None:
            qt.QMessageBox.warning(main_window, "In-text help", error or "The sentence could not be changed.")
            return
        current_reading = updated_reading
        display_reading()

    previous_button.clicked.connect(lambda: apply_navigation(learning.previous_sentence))
    restart_button.clicked.connect(lambda: apply_navigation(learning.restart_text))
    next_button.clicked.connect(lambda: apply_navigation(learning.next_sentence))
    back_button.clicked.connect(lambda: _show_text_units(main_window, learning, deck_id))
    sentence_view.anchorClicked.connect(lambda url: select_surface_form(unquote(url.toString())))
    _install_plugin_view(main_window, page)
    display_reading()
