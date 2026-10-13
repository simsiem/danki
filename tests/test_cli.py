from pathlib import Path

from danki import cli


class FakeConsole:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def print(self, *args: object, **_kwargs: object) -> None:
        self.messages.append(" ".join(str(arg) for arg in args))


def test_missing_input_returns_nonzero(tmp_path: Path, monkeypatch) -> None:
    fake_console = FakeConsole()
    monkeypatch.setattr(cli, "console", fake_console)

    missing_input = tmp_path / "missing.html"
    exit_status = cli.convert([missing_input], tmp_path / "output.csv")

    assert exit_status == 1
    assert fake_console.messages == [f"Error: input file not found: {missing_input}"]


def test_bad_paragraph_is_skipped_and_conversion_continues(tmp_path: Path, monkeypatch) -> None:
    fake_console = FakeConsole()
    monkeypatch.setattr(cli, "console", fake_console)

    input_file = tmp_path / "book.html"
    input_file.write_text(
        '<html xmlns="http://www.w3.org/1999/xhtml"><body>'
        "<p>not a vocabulary paragraph</p>"
        "<p><span>amo</span><span>    love </span><span>1</span></p>"
        "</body></html>",
        encoding="utf-8",
    )
    output_file = tmp_path / "output.csv"

    exit_status = cli.convert([input_file], output_file)

    assert exit_status == 0
    assert "Failed parsing of paragraph 1" in fake_console.messages[0]
    assert "Converted 1 entries." in fake_console.messages
    assert "amo,amo,amo" in output_file.read_text(encoding="utf-8")
