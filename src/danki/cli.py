import csv
from pathlib import Path
from typing import TYPE_CHECKING
from xml.etree import ElementTree as ET

from cyclopts import App

from danki import converter
from danki.console import console

if TYPE_CHECKING:
    from io import TextIOWrapper

app = App(help_format="restructuredtext")


@app.command()
def convert(
    inputs: list[Path], /, output_file: Path, *, book: str | None = None, print_merge: bool = False
) -> None:
    """Convert a Campus C1 vocabulary list to a Danki CSV file.

    Parameters
    ----------
    inputs
        List of input files in CSV, XHTML or FODT format
    book
        Reference book indentifier
    output_file
        Output CSV path
    """

    _book = book if book is not None else inputs[0].stem

    csv_files: list[TextIOWrapper] = []
    readers: list[converter.Reader] = []
    try:
        for input_file in inputs:
            if not input_file.exists():
                console.print(f"Error: input file not found: {input_file}")
                return 1
            ext = input_file.suffix.lower()
            if ext == ".csv":
                f = input_file.open("r", encoding="utf-8", newline="")
                csv_files.append(f)
                reader = csv.DictReader(f)
                reader.source_name = input_file.name
                readers.append(reader)
            elif ext in (".fodt", ".html", ".xhtml"):
                tree = ET.parse(input_file)  # noqa: S314
                tree.source_name = input_file.name
                readers.append(tree)
            else:
                console.print(f"Error: unsupported input file type: {input_file}")
                return 1

        with output_file.open("w", encoding="utf-8", newline="") as output_file_fd:
            converter.convert(readers, output_file_fd, _book, console, show_merge_messages=print_merge)

    except Exception as e:  # noqa: BLE001
        console.print(f"Error: {e}")
        return 1

    finally:
        for f in csv_files:
            f.close()


if __name__ == "__main__":
    app()
