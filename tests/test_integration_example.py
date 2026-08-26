import csv
import io
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from danki import converter


class SimpleConsole:
    def __init__(self):
        self.messages = []

    def print(self, *args, **_):
        self.messages.append(" ".join(str(a) for a in args))


@pytest.mark.parametrize(
    ("file", "row_count"),
    [("tests/test_book_C1.html", 153), ("tests/test_book_C2.fodt", 30)],
)
def test_integration_convert_example(file, row_count):
    input_path = Path(file)
    assert input_path.exists()

    tree = ET.parse(str(input_path))
    out = io.StringIO()
    console = SimpleConsole()

    converter.convert(tree, out, "example_school_book_input", console)

    out.seek(0)
    reader = csv.DictReader(out)
    rows = list(reader)

    # Expect the converter to produce the extracted entries from the example file
    assert len(rows) == row_count
    assert reader.fieldnames is not None
    assert "Headword" in reader.fieldnames
    # At least one Top500 tag should be present
    assert any("Top500" in (r.get("Tags") or "") for r in rows)
