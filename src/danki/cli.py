from pathlib import Path
from xml.etree import ElementTree as ET

from cyclopts import App

from danki import converter
from danki.console import console

app = App(help_format="restructuredtext")


@app.command()
def convert(input_file: Path, /, *, book: str | None = None, output_file: Path | None = None) -> None:
    """Convert a Campus C1 vocabulary list to a Danki CSV file.

    Parameters
    ----------
    input_file
        Input XHTML file derived from the published docx file
    book
        Reference book indentifier
    output_file
        Output CSV path
    """
    if not input_file.exists():
        console.print(f"Error: input file not found: {input_file}")
        return 1

    _output_file = output_file if output_file is not None else input_file.with_suffix(".csv")
    _book = book if book is not None else input_file.stem

    try:
        tree = ET.parse(str(input_file))  # noqa: S314
        with _output_file.open("w", encoding="utf-8", newline="") as output_file_fd:
            return converter.convert(tree, output_file_fd, _book, console)
    except Exception as e:  # noqa: BLE001
        console.print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    app()
