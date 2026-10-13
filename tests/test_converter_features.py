import csv
import io
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from danki import converter

FEATURES_DIRECTORY = Path(__file__).parents[1] / "docs" / "features" / "converter"
CANONICAL_FIELDS = [
    "Headword",
    "FullFormDisplay",
    "FullFormNormalized",
    "PartOfSpeech",
    "NotesForeign",
    "Meanings",
    "NumberOfMeanings",
    "NotesNative",
    "MnemonicHint",
    "PronunciationText",
    "AudioUrl",
    "ReferenceBook",
    "ReferenceSection",
    "Exercise1Front",
    "Exercise1Back",
    "Exercise2Front",
    "Exercise2Back",
    "Exercise3Front",
    "Exercise3Back",
    "Tags",
]


scenarios(str(FEATURES_DIRECTORY))


class FakeConsole:
    def __init__(self):
        self.messages = []

    def print(self, *args, **_):
        # simple join for ease of assertions
        self.messages.append(" ".join(str(a) for a in args))


@dataclass
class ConversionResult:
    rows: list[str]
    fieldnames: list[str]
    messages: list[str]


@pytest.fixture
def conversion_context() -> dict[str, object]:
    return {}


def _html_reader(body: str, source_name: str | None = None):
    xml = (
        """\
<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
    <head><style>
        .text-T13{ color:#0070c0; font-size:10.5pt; font-weight:bold; }
    </style></head>
    <body>
"""
        + body
        + """
    </body>
</html>
"""
    )
    tree = ET.ElementTree(ET.fromstring(xml))
    if source_name:
        tree.source_name = source_name
    return tree


def _fodt_reader(body: str):
    xml = (
        """\
<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:loext="urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0" xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0">
 <office:automatic-styles>
  <style:style style:name="T11" style:family="text">
   <style:text-properties fo:color="#0070c0" loext:opacity="100%" fo:font-family="Calibri" style:font-family-generic="swiss" style:font-pitch="variable" fo:font-size="10.5pt" fo:font-weight="bold" style:font-family-asian="MercuryTextG1-Roman" style:font-family-generic-asian="system" style:font-pitch-asian="variable" style:font-size-asian="10.5pt" style:font-weight-asian="bold" style:font-family-complex="MercuryTextG1-Roman" style:font-family-generic-complex="system" style:font-pitch-complex="variable" style:font-size-complex="10.5pt"/>
  </style:style>
 </office:automatic-styles>
 <office:body>
  <office:text text:use-soft-page-breaks="true">
"""
        + body
        + """
  </office:text>
 </office:body>
</office:document>
"""
    )
    return ET.ElementTree(ET.fromstring(xml))


def _csv_reader(body: str):
    return csv.DictReader(io.StringIO(body))


def _convert(readers, book: str, *, show_merge_messages: bool = False) -> ConversionResult:
    output = io.StringIO()
    console = FakeConsole()
    converter.convert(readers, output, book, console, show_merge_messages=show_merge_messages)
    output_lines = output.getvalue().splitlines()
    return ConversionResult(output_lines[1:], output_lines[0].split(","), console.messages)


def _store_reader(conversion_context, reader):
    conversion_context.setdefault("readers", []).append(reader)


@given(parsers.re(r'the HTML body(?: with filename "(?P<name>[^"]+)")?:'))
def html_body(conversion_context, docstring, name=None):
    _store_reader(conversion_context, _html_reader(docstring, name))


@given("the FODT body:")
def fodt_body(conversion_context, docstring):
    _store_reader(conversion_context, _fodt_reader(docstring))


@given("the CSV input:")
def csv_input(conversion_context, docstring):
    _store_reader(conversion_context, _csv_reader(docstring))
    conversion_context["expected_csv_rows"] = docstring.splitlines()[1:]


@given(parsers.parse('the input file "{name}"'))
def input_file(conversion_context, name):
    _store_reader(conversion_context, ET.parse(name))


@when(
    parsers.re(
        r'Danki converts the input(?: with book "(?P<book>[^"]*)")?'
        r"(?: showing (?P<merge_mode>merge|no merge) messages)?$"
    ),
    target_fixture="conversion_result",
)
def convert_input(conversion_context, book=None, merge_mode=None):
    return _convert(conversion_context["readers"], book or "", show_merge_messages=merge_mode == "merge")


@then("it outputs a Danki CSV file with the body:")
def danki_csv_file(conversion_result, docstring):
    assert conversion_result.fieldnames == CANONICAL_FIELDS
    assert conversion_result.rows == docstring.splitlines()


@then("no mismatch warning is reported")
def no_mismatch_warning(conversion_result):
    assert not any("Mismatch for" in message for message in conversion_result.messages)


@then("a mismatch warning is reported")
def mismatch_warning(conversion_result):
    assert any("Mismatch for" in message for message in conversion_result.messages)


@then("a merge is reported")
def merge_reported(conversion_result):
    assert any("Merge " in message for message in conversion_result.messages)


@then(parsers.parse("the output contains {count:d} vocabulary entries"))
def output_entry_count(conversion_result, count):
    assert len(conversion_result.rows) == count


@then(parsers.parse('the output contains the canonical CSV field "{field}"'))
def output_has_csv_field(conversion_result, field):
    assert field in conversion_result.fieldnames


@then(parsers.parse('at least one output entry has the tag "{tag}"'))
def output_has_tag(conversion_result, tag):
    rows = csv.DictReader(io.StringIO("\n".join([",".join(CANONICAL_FIELDS), *conversion_result.rows])))
    assert any(tag in (row["Tags"] or "") for row in rows)


@then("the expected output is empty")
def output_empty(conversion_result):
    assert conversion_result.rows == []


@then("a parsing warning is reported for the paragraph")
def parsing_warning(conversion_result):
    assert any("Failed parsing" in message for message in conversion_result.messages)


@then("the output CSV is identical to the input CSV")
def csv_output_is_identical(conversion_context, conversion_result):
    assert conversion_result.rows == conversion_context["expected_csv_rows"]


@then("the console output is:")
def console_output(conversion_result, docstring):
    assert conversion_result.messages == docstring.splitlines()
