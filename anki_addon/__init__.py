"""Anki add-on loader for the in-text help workflow."""

import sys
from importlib import import_module
from pathlib import Path

addon_directory = Path(__file__).resolve().parent
for import_directory in (addon_directory, addon_directory.parent / "src"):
    if import_directory.is_dir() and str(import_directory) not in sys.path:
        sys.path.insert(0, str(import_directory))

import_module("danki.anki_addon").initialize()
