"""Build a standalone Anki add-on folder from the Danki source tree."""

import argparse
import shutil
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
ADDON_MODULES = ("anki_addon.py", "anki_storage.py", "textunit.py")


def build_anki_addon(destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REPOSITORY_ROOT / "anki_addon" / "__init__.py", destination / "__init__.py")

    bundled_package = destination / "danki"
    bundled_package.mkdir(exist_ok=True)
    package_source = REPOSITORY_ROOT / "src" / "danki"
    for module_name in ("__init__.py", *ADDON_MODULES):
        shutil.copy2(package_source / module_name, bundled_package / module_name)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the standalone Danki Anki add-on folder.")
    parser.add_argument("destination", type=Path, help="target directory inside Anki's addons21 directory")
    arguments = parser.parse_args()
    build_anki_addon(arguments.destination)


if __name__ == "__main__":
    main()
