import io
from xml.etree import ElementTree as ET

import pytest

from danki import converter


class _FakeConsole:
    def __init__(self):
        self.messages = []

    def print(self, *args, **_):
        # simple join for ease of assertions
        self.messages.append(" ".join(str(a) for a in args))


def _make_tree(body: str) -> ET.ElementTree:
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        """
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
    return ET.ElementTree(ET.fromstring(xml))


def _run_conversion(body, expected_csv, book):
    expected_head_line = "Headword,FullFormDisplay,FullFormNormalized,PartOfSpeech,NotesForeign,Meanings,NumberOfMeanings,NotesNative,MnemonicHint,PronunciationText,AudioUrl,ReferenceBook,ReferenceSection,Exercise1Front,Exercise1Back,Exercise2Front,Exercise2Back,Exercise3Front,Exercise3Back,Tags"
    tree = _make_tree(body)
    out = io.StringIO()
    console = _FakeConsole()

    converter.convert(tree, out, book, console)

    lines = out.getvalue().splitlines()
    expected_lines = [expected_head_line, *expected_csv.splitlines()]
    assert len(lines) == len(expected_lines)
    for line, expected_line in zip(lines, expected_lines, strict=False):
        assert line == expected_line

    return console


#     1          2                3              4             5          6            7              8            9             10            11           12               13             14            15             16            17             18            19       20
# Headword,FullFormDisplay,FullFormNormalized,PartOfSpeech,NotesForeign,Meanings,NumberOfMeanings,NotesNative,MnemonicHint,PronunciationText,AudioUrl,ReferenceBook,ReferenceSection,Exercise1Front,Exercise1Back,Exercise2Front,Exercise2Back,Exercise3Front,Exercise3Back,Tags
@pytest.mark.parametrize(
    ("body", "expected_csv_row"),
    [
        (
            "<p><span>auxilium</span>    die Hilfe15</p>",
            #    1        2        3          6     7      12   13
            "auxilium,auxilium,auxilium,,,die Hilfe,1,,,,,book1,15,,,,,,,",
        ),
        (
            "<p><span>ā / ab</span> Präp. m. Abl.    von, von ... her16</p>",
            'a / ab,ā / ab,a / ab,Präposition,Präp. m. Abl.,"von, von ... her",2,,,,,book1,16,,,,,,,',
        ),
        (
            "<p><span>dum</span>  Subj.    während, solange, bis19</p>",
            'dum,dum,dum,Subjunktion,Subj.,"während, solange, bis",3,,,,,book1,19,,,,,,,',
        ),
        (
            "<p><span>iuvenis, iuvenis</span> m    der junge Mann; Adj. jung<span>32</span></p>",
            'iuvenis,"iuvenis, iuvenis","iuvenis, iuvenis",Nomen,m,der junge Mann; Adj. jung,2,,,,,book1,32,,,,,,,',
        ),
        (
            "<p><span>līberī, līberōrum</span> m Pl.    die Kinder<span>26</span></p>",
            'liberi,"līberī, līberōrum","liberi, liberorum",Nomen,m Pl.,die Kinder,1,,,,,book1,26,,,,,,,',
        ),
        (
            "<p><span>ostendere, ostendō, ostendī</span>    zeigen, erklären<span>16. 28</span></p>",
            'ostendere,"ostendere, ostendō, ostendī","ostendere, ostendo, ostendi",,,"zeigen, erklären",2,,,,,book1,16;28,,,,,,,',
        ),
        (
            '<p class="paragraph-P5"><span class="text-T13">auxilium</span><span class="text-T14">    die Hilfe</span><span class="text-T15">15</span></p>',  # noqa: RUF001
            "auxilium,auxilium,auxilium,,,die Hilfe,1,,,,,book1,15,,,,,,,Top500",
        ),
        (
            '<p class="paragraph-P5"><span class="text-T13">ā / ab</span><span class="text-T6"> </span><span class="text-T7">Präp. m. Abl.    </span><span class="text-T8">von, von ... her</span><span class="text-T9">16</span></p>',  # noqa: RUF001
            'a / ab,ā / ab,a / ab,Präposition,Präp. m. Abl.,"von, von ... her",2,,,,,book1,16,,,,,,,Top500',
        ),
        (
            '<p class="paragraph-P6"><span class="text-T10">iuvenis, iuvenis</span><span class="text-T11">  </span><span class="text-T22">m</span><span class="text-T11">    der junge Mann; Adj. jung</span><span class="text-T12">32</span></p>',  # noqa: RUF001
            'iuvenis,"iuvenis, iuvenis","iuvenis, iuvenis",Nomen,m,der junge Mann; Adj. jung,2,,,,,book1,32,,,,,,,',
        ),
        (
            '<p class="paragraph-P6"><span class="text-T21">līberī, līberōrum</span><span class="text-T11">  </span><span class="text-T22">m Pl.</span><span class="text-T11">    die Kinder</span><span class="text-T12">26</span></p>',  # noqa: RUF001
            'liberi,"līberī, līberōrum","liberi, liberorum",Nomen,m Pl.,die Kinder,1,,,,,book1,26,,,,,,,',
        ),
        (
            '<p class="paragraph-P6"><span class="text-T13">ostendere, ostendō, ostendī</span><span class="text-T11">    zeigen, erklären</span><span class="text-T12">16. 28</span></p>',  # noqa: RUF001
            'ostendere,"ostendere, ostendō, ostendī","ostendere, ostendo, ostendi",,,"zeigen, erklären",2,,,,,book1,16;28,,,,,,,Top500',
        ),
        (
            '<p class="paragraph-P6"><span class="text-T21">dum</span><span class="text-T11">  </span><span class="text-T22">Subj.</span><span class="text-T11">    während, solange, bis</span><span class="text-T12">19</span></p>',  # noqa: RUF001
            'dum,dum,dum,Subjunktion,Subj.,"während, solange, bis",3,,,,,book1,19,,,,,,,',
        ),
        (
            '<p class="paragraph-P5"><span class="text-T10">comes, comitis</span><span class="text-T11">  </span><span class="text-T22">m/f</span><span class="text-T11">    der (die) Begleiter(in), der Gefährte, die Gefährtin</span><span class="text-T12">32</span></p>',  # noqa: RUF001
            'comes,"comes, comitis","comes, comitis",Nomen,m/f,"der (die) Begleiter(in), der Gefährte, die Gefährtin",3,,,,,book1,32,,,,,,,',
        ),
        (
            '<p class="paragraph-P1"><span class="text-T5">-que</span><span class="text-T6">  (angehängt)    und</span><span class="text-T8">14</span></p>',  # noqa: RUF001
            "-que,-que,-que,,(angehängt),und,1,,,,,book1,14,,,,,,,",
        ),
        (
            '<p class="paragraph-P6"><span class="text-T27">tamquam</span><span class="text-T6">   </span><span class="text-T7">Adv.</span><span class="text-T6">    wie</span><span class="text-T8">32</span></p>',  # noqa: RUF001
            "tamquam,tamquam,tamquam,Adverb,Adv.,wie,1,,,,,book1,32,,,,,,,",
        ),
        (
            '<p class="paragraph-P1"><span class="text-T17">paulō post</span><span class="text-T6">    (ein) wenig später</span><span class="text-T8">26</span></p>',  # noqa: RUF001
            "paulo post,paulō post,paulo post,,,(ein) wenig später,1,,,,,book1,26,,,,,,,",
        ),
        (
            '<p class="paragraph-P6"><span class="text-T13">et ... et</span><span class="text-T6">    sowohl ... als auch</span><span class="text-T8">35</span></p>',  # noqa: RUF001
            "et ... et,et ... et,et ... et,,,sowohl ... als auch,1,,,,,book1,35,,,,,,,Top500",
        ),
    ],
)
def test_single_paragraph_variants(body, expected_csv_row):
    _run_conversion(body, expected_csv_row, "book1")


def test_duplicate_mismatch_logs_and_keep_first():
    body = """\
<p><span>ācer</span>   energisch 32</p>
<p><span>ācer</span>   anders 32</p>
"""
    expected_csv = "acer,ācer,acer,,,energisch,1,,,,,book1,32,,,,,,,"

    console = _run_conversion(body, expected_csv, "book1")

    # mismatch warning present
    found = any("Mismatch for" in m for m in console.messages)
    assert found, f"Expected mismatch log, got: {console.messages}"


def test_non_matching_paragraph_logged():
    # only two spaces -> should not match (requires 3+)
    body = "<p>testword  not-enough-spaces 32</p>"

    console = _run_conversion(body, "", "")

    found = any(m.startswith("Info: paragraph") for m in console.messages)
    assert found, f"Expected info about non-matching paragraph, got: {console.messages}"
