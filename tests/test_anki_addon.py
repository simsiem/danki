from types import SimpleNamespace

from danki import anki_addon
from scripts.build_anki_addon import build_anki_addon


def test_initialize_registers_the_in_text_help_menu_action(monkeypatch) -> None:
    callbacks = []
    actions = []

    class Hook:
        def append(self, callback) -> None:
            callbacks.append(callback)

    class Signal:
        def connect(self, callback) -> None:
            self.callback = callback

    class Action:
        def __init__(self, label: str, _parent) -> None:
            self.label = label
            self.triggered = Signal()

    class Menu:
        def addAction(self, action) -> None:  # noqa: N802
            actions.append(action)

    fake_aqt = SimpleNamespace(
        gui_hooks=SimpleNamespace(main_window_did_init=Hook()),
        mw=SimpleNamespace(form=SimpleNamespace(menuTools=Menu())),
    )
    fake_qt = SimpleNamespace(QAction=Action)
    monkeypatch.setattr(
        anki_addon,
        "import_module",
        lambda module_name: {"aqt": fake_aqt, "aqt.qt": fake_qt}[module_name],
    )

    anki_addon.initialize()
    callbacks[0]()

    assert [action.label for action in actions] == ["In-text help"]


def test_addon_builder_bundles_only_the_runtime_modules(tmp_path) -> None:
    destination = tmp_path / "danki_in_text_help"
    build_anki_addon(destination)

    assert (destination / "__init__.py").is_file()
    assert {path.name for path in (destination / "danki").iterdir()} == {
        "__init__.py",
        "anki_addon.py",
        "anki_storage.py",
        "textunit.py",
    }
