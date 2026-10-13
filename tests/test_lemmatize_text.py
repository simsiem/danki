import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

CHECKER = Path(__file__).parents[1] / ".agents" / "skills" / "lemmatize-text" / "check_vocab.py"


@pytest.mark.parametrize(
    ("entry", "text", "expected_error"),
    [
        ({"surfaceForm": "amo", "headwords": ["amo"]}, "amo", False),
        ({"surfaceForm": "ignotus", "notes": "a stranger"}, "ignotus", False),
        ({"surfaceForm": "amo", "headwords": ["amo"], "notes": "love"}, "amo", True),
        ({"surfaceForm": "amo"}, "amo", True),
    ],
)
def test_checker_requires_exactly_one_entry_field(tmp_path, entry, text, expected_error):
    json_path = tmp_path / "text.json"
    csv_path = tmp_path / "vocab.csv"
    json_path.write_text(
        json.dumps({"text": text, "vocabularyEntries": [entry]}),
        encoding="utf-8",
    )
    with csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["Headword"])
        writer.writeheader()
        writer.writerow({"Headword": "amo"})

    result = subprocess.run(
        [sys.executable, str(CHECKER), str(json_path), str(csv_path)],
        capture_output=True,
        check=False,
        text=True,
    )

    assert (result.returncode != 0) is expected_error
    assert ("invalid entry fields:" in result.stdout) is expected_error


@pytest.mark.parametrize(
    ("entry", "expected_message"),
    [
        (None, "invalid entry: vocabularyEntries[0] must be an object"),
        ({"headwords": ["amo"]}, "must have a non-empty string 'surfaceForm'"),
        ({"surfaceForm": "amo", "headwords": "amo"}, "'headwords' must be an array of non-empty strings"),
    ],
)
def test_checker_reports_malformed_entries(tmp_path, entry, expected_message):
    json_path = tmp_path / "text.json"
    csv_path = tmp_path / "vocab.csv"
    json_path.write_text(
        json.dumps({"text": "amo", "vocabularyEntries": [entry]}),
        encoding="utf-8",
    )
    with csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["Headword"])
        writer.writeheader()
        writer.writerow({"Headword": "amo"})

    result = subprocess.run(
        [sys.executable, str(CHECKER), str(json_path), str(csv_path)],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode != 0
    assert expected_message in result.stdout
    assert "Traceback" not in result.stderr
