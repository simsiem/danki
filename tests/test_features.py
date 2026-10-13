import csv
import io
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from danki import converter
from tests.convert_helpers import FakeConsole, make_fodt, make_html


FEATURES_DIRECTORY = Path(__file__).parents[1] / "docs" / "features"
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


@dataclass
class ConversionResult:
    rows: list[str]
    fieldnames: list[str]
    messages: list[str]


@pytest.fixture
def conversion_context() -> dict[str, object]:
    return {}


def _html_reader(body: str, source_name: str | None = None):
    tree = make_html(body)
    if source_name:
        tree.source_name = source_name
    return tree


def _fodt_reader(body: str):
    return make_fodt(body)


def _csv_reader(body: str):
    return csv.DictReader(io.StringIO(body))


def _convert(readers, book: str, show_merge_messages: bool = False) -> ConversionResult:
    output = io.StringIO()
    console = FakeConsole()
    converter.convert(readers, output, book, console, show_merge_messages=show_merge_messages)
    output_lines = output.getvalue().splitlines()
    return ConversionResult(output_lines[1:], output_lines[0].split(","), console.messages)


@given("the HTML body:")
def html_body(conversion_context, docstring):
    html_reader = _html_reader(docstring)
    conversion_context["html_reader"] = html_reader
    if "readers" not in conversion_context:
        conversion_context["readers"] = [html_reader]


@given("the FODT body:")
def fodt_body(conversion_context, docstring):
    fodt_reader = _fodt_reader(docstring)
    conversion_context["fodt_reader"] = fodt_reader
    if "readers" not in conversion_context:
        conversion_context["readers"] = [fodt_reader]


@given("the CSV input:")
def csv_input(conversion_context, docstring):
    conversion_context["readers"] = [_csv_reader(docstring)]
    conversion_context["expected_csv_rows"] = docstring.splitlines()[1:]


@given(parsers.parse('the HTML input file "{name}" with body:'))
def named_html_body(conversion_context, name, docstring):
    conversion_context.setdefault("named_readers", {})[name] = _html_reader(docstring, name)


@given("the HTML input file " + '"tests/test_book_C1.html"')
def html_input_file(conversion_context):
    conversion_context["readers"] = [ET.parse("tests/test_book_C1.html")]


@given("the FODT input file " + '"tests/test_book_C2.fodt"')
def fodt_input_file(conversion_context):
    conversion_context["readers"] = [ET.parse("tests/test_book_C2.fodt")]


@when(parsers.parse('Danki converts it with book "{book}"'), target_fixture="conversion_result")
@when(parsers.parse('Danki converts the input with book "{book}"'), target_fixture="conversion_result")
def convert_input(conversion_context, book):
    return _convert(conversion_context["readers"], book)


@when("Danki converts the input", target_fixture="conversion_result")
def convert_input_without_book(conversion_context):
    return _convert(conversion_context["readers"], "")


@when(
    parsers.parse('Danki converts it with book "{book}" showing merge messages'),
    target_fixture="conversion_result",
)
def convert_with_merge_messages(conversion_context, book):
    return _convert(conversion_context["readers"], book, show_merge_messages=True)


@when(
    parsers.parse(
        'Danki converts the CSV input, then the FODT input, then the HTML input with book "{book}"'
    ),
    target_fixture="conversion_result",
)
def convert_multiple_formats(conversion_context, book):
    readers = [
        conversion_context["readers"][0],
        conversion_context["fodt_reader"],
        conversion_context["html_reader"],
    ]
    return _convert(readers, book)


@when(
    parsers.parse('Danki converts "{first_name}", then "{second_name}" with book "{book}" showing merge messages'),
    target_fixture="conversion_result",
)
def convert_named_files_with_merges(conversion_context, first_name, second_name, book):
    named_readers = conversion_context["named_readers"]
    return _convert([named_readers[first_name], named_readers[second_name]], book, show_merge_messages=True)


@when(
    parsers.parse(
        'Danki converts "{first_name}", then "{second_name}" with book "{book}" showing no merge messages'
    ),
    target_fixture="conversion_result",
)
def convert_named_files_without_merges(conversion_context, first_name, second_name, book):
    named_readers = conversion_context["named_readers"]
    return _convert([named_readers[first_name], named_readers[second_name]], book)


@then("it outputs the CSV body:")
def csv_body(conversion_result, docstring):
    assert conversion_result.rows == docstring.splitlines()


@then("the output uses the canonical CSV fields")
def canonical_csv_fields(conversion_result):
    assert conversion_result.fieldnames == CANONICAL_FIELDS


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