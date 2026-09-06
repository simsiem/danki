import csv
import io

import pytest

from danki import converter
from tests.convert_helpers import FakeConsole, make_fodt, make_html


def _run_conversion(body: str, expected_csv: str, book: str) -> FakeConsole:
    expected_head_line = "Headword,FullFormDisplay,FullFormNormalized,PartOfSpeech,NotesForeign,Meanings,NumberOfMeanings,NotesNative,MnemonicHint,PronunciationText,AudioUrl,ReferenceBook,ReferenceSection,Exercise1Front,Exercise1Back,Exercise2Front,Exercise2Back,Exercise3Front,Exercise3Back,Tags"
    out = io.StringIO()
    console = FakeConsole()

    if body.startswith("<p"):
        tree = make_html(body)
    elif body.startswith("<text:p"):
        tree = make_fodt(body)
    else:
        body_snippet = body[: min(len(body), 10)]
        msg = f"Unknown type of body for test case. Body starts with {body_snippet}"
        raise ValueError(msg)

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
            #    1              2                  3            4        6     7      12   13
            'auxilium,"auxilium, auxilii","auxilium, auxilii",Nomen,,die Hilfe,1,,,,,book1,15,,,,,,,',
        ),
        (
            "<p><span>amīca</span>    die Freundin15</p>",
            'amica,"amīca, amīcae","amica, amicae",Nomen,,die Freundin,1,,,,,book1,15,,,,,,,',
        ),
        (
            "<p><span>amīcus</span>    der Freund15</p>",
            'amicus,"amīcus, amīci","amicus, amici",Nomen,,der Freund,1,,,,,book1,15,,,,,,,',
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
            'ostendere,"ostendere, ostendō, ostendī","ostendere, ostendo, ostendi",Verb,,"zeigen, erklären",2,,,,,book1,16;28,,,,,,,',
        ),
        (
            "<p><span>beātus, beāta,beātum</span>    glücklich, reich36</p>",
            'beatus,"beātus, a, um","beatus, a, um",Adjektiv,,"glücklich, reich",2,,,,,book1,36,,,,,,,',
        ),
        (
            '<p class="paragraph-P5"><span class="text-T13">auxilium</span><span class="text-T14">    die Hilfe</span><span class="text-T15">15</span></p>',  # noqa: RUF001
            'auxilium,"auxilium, auxilii","auxilium, auxilii",Nomen,,die Hilfe,1,,,,,book1,15,,,,,,,Top500',
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
            'ostendere,"ostendere, ostendō, ostendī","ostendere, ostendo, ostendi",Verb,,"zeigen, erklären",2,,,,,book1,16;28,,,,,,,Top500',
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
            "-que,-que,-que,,angehängt,und,1,,,,,book1,14,,,,,,,",
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
        (
            '<text:p text:style-name="P25" loext:marker-style-name="T16"><text:span text:style-name="T17">Alexander, Alexandrī</text:span><text:span text:style-name="T19"> <text:s text:c="2"/></text:span><text:span text:style-name="T20"><text:s/>Alexander der Große </text:span><text:span text:style-name="T21">(König von Makedonien)</text:span><text:span text:style-name="T22">38</text:span></text:p>',
            'Alexander,"Alexander, Alexandrī","Alexander, Alexandri",,,Alexander der Große (König von Makedonien),1,,,,,book1,38,,,,,,,',
        ),
        (
            '<text:p text:style-name="P25" loext:marker-style-name="T24"><text:span text:style-name="T11">bene</text:span><text:span text:style-name="T20"> </text:span><text:span text:style-name="T21">Adv. <text:s text:c="3"/></text:span><text:span text:style-name="T20">gut</text:span><text:span text:style-name="T22">4</text:span></text:p>',
            "bene,bene,bene,Adverb,Adv.,gut,1,,,,,book1,4,,,,,,,Top500",
        ),
    ],
)
def test_single_paragraph_variants(body, expected_csv_row):
    console = _run_conversion(body, expected_csv_row, "book1")

    is_mismatch = any("Mismatch for" in m for m in console.messages)
    assert not is_mismatch, f"Conversion free of warnings, got: {console.messages}"


@pytest.mark.parametrize(
    ("body", "expected_csv"),
    [
        (
            # Mismatch in Meanings
            """\
<p><span>ācer</span>   energisch 32</p>
<p><span>et</span>    und 5</p>
<p><span>ācer</span>   anders 32</p>
""",
            """\
acer,ācer,acer,,,energisch,1,,,,,book1,32,,,,,,,
et,et,et,,,und,1,,,,,book1,5,,,,,,,
""",
        ),
        (
            # Mismatch in Meanings
            """\
<p><span>ācer</span>   energisch 32</p>
<p><span>et</span>    und 5</p>
<p><span>ācer</span>   energisch 3</p>
""",
            """\
acer,ācer,acer,,,energisch,1,,,,,book1,32,,,,,,,
et,et,et,,,und,1,,,,,book1,5,,,,,,,
""",
        ),
        (
            # Mismatch in joint grammatical subform
            """\
<p><span>audīre, audiō</span>    hören, lernen32</p>
<p><span>audīre, audio, audīvī, audītum</span>    hören, lernen32</p>
""",
            'audire,"audīre, audiō","audire, audio",Verb,,"hören, lernen",2,,,,,book1,32,,,,,,,',
        ),
        (
            # Correct mismatch behaviour if new entry offers better FullFormDisplay.
            # Expanded FullFormDisplay taken from new entry, but other values taken from old entry.
            # Report a mismatch in Meanings.
            """\
<p><span>audīre, audiō</span>    hören, lernen32</p>
<p><span>audīre, audiō, audīvī, audītum</span>    hören32</p>
""",
            'audire,"audīre, audiō, audīvī, audītum","audire, audio, audivi, auditum",Verb,,"hören, lernen",2,,,,,book1,32,,,,,,,',
        ),
    ],
)
def test_duplicate_mismatch_logs_and_keep_first(body, expected_csv):
    console = _run_conversion(body, expected_csv, "book1")

    is_mismatch = any("Mismatch for" in m for m in console.messages)
    assert is_mismatch, f"Expected mismatch log, got: {console.messages}"


@pytest.mark.parametrize(
    ("body", "expected_csv"),
    [
        (
            # Correct grammatical forms in second paragraph. Keep second paragraph.
            """\
<p><span>audīre, audiō</span>    hören, lernen32</p>
<p><span>audīre, audiō, audīvī, audītum</span>    hören, lernen32</p>
""",
            'audire,"audīre, audiō, audīvī, audītum","audire, audio, audivi, auditum",Verb,,"hören, lernen",2,,,,,book1,32,,,,,,,',
        ),
        (
            # Correct grammatical forms in first paragraph. Keep first paragraph.
            """\
<p><span>Rōma, Rōmae</span>    die Stadt Rom32</p>
<p><span>Rōma</span>    die Stadt Rom32</p>
""",
            'Roma,"Rōma, Rōmae","Roma, Romae",Nomen,,die Stadt Rom,1,,,,,book1,32,,,,,,,',
        ),
        (
            # Extended section list in second paragraph. Keep second paragraph.
            """\
<p><span>Rōma, Rōmae</span>    die Stadt Rom32</p>
<p><span>Rōma, Rōmae</span>    die Stadt Rom32.21</p>
""",
            'Roma,"Rōma, Rōmae","Roma, Romae",Nomen,,die Stadt Rom,1,,,,,book1,21;32,,,,,,,',
        ),
    ],
)
def test_duplicate_merge(body, expected_csv):
    console = _run_conversion(body, expected_csv, "book1")

    is_mismatch = any("Mismatch for" in m for m in console.messages)
    assert not is_mismatch, f"Conversion free of warnings, got: {console.messages}"
    is_merge = any("Merge" in m for m in console.messages)
    assert is_merge, f"Expected info about a merge, got: {console.messages}"


def test_non_matching_paragraph_logged():
    # only two spaces -> should not match (requires 3+)
    body = "<p>testword  not-enough-spaces 32</p>"

    console = _run_conversion(body, "", "")

    found = any(m.startswith("WARNING: Paragraph") for m in console.messages)
    assert found, f"Expected warning about non-matching paragraph, got: {console.messages}"


def test_single_csv_passthrough_matches_reference():
    in_str = """\
Headword,FullFormDisplay,FullFormNormalized,PartOfSpeech,NotesForeign,Meanings,NumberOfMeanings,NotesNative,MnemonicHint,PronunciationText,AudioUrl,ReferenceBook,ReferenceSection,Exercise1Front,Exercise1Back,Exercise2Front,Exercise2Back,Exercise3Front,Exercise3Back,Tags
-ne,-ne,-ne,,,Partikel im dir. Fragesatz (unübersetzt),1,,,,,Campus C1,13,,,,,,,Top500
a / ab,ā / ab,a / ab,Präposition,Präp. m. Abl.,"von, von ... her",2,,,,,Campus C1,16,,,,,,,Top500
abire,"abīre, abeō, abiī","abire, abeo, abii",Verb,B,weggehen,1,C,D,E,F,Campus C1,37,G,H,I,J,K,L,Top500
Aeneas,"Aenēās, Aenēae","Aeneas, Aeneae",Nomen,m,Äneas (Trojaner und Stammvater der Römer),1,,,,,Campus C1,30,,,,,,,
Romulus / Remus,Rōmulus / Remus,Romulus / Remus,Nomen,,Romulus / Remus,1,Zwillingsbrüder und sagenhafte Gründer Roms,,,,Campus C1,32,,,,,,,
Tarquinius Superbus,Tarquinius Superbus,Tarquinius Superbus,Nomen,,Tarquinius Superbus,1,Letzter etruskischer König von Rom,,,,Campus C1,36,,,,,,,
vox,"vōx, vōcis","vox, vocis",Nomen,f,"die Stimme, die Äußerung, der Laut",3,,,,,Campus C1,25,,,,,,,Top500
"""
    reader = csv.DictReader(io.StringIO(in_str))
    # open the reference CSV as input and also as expected output
    out = io.StringIO()
    console = FakeConsole()

    # pass the open file as the only reader (convert accepts iterable of readers)
    converter.convert([reader], out, "Campus C1", console)

    got = out.getvalue().splitlines()
    assert got == in_str.splitlines(), f"Expected output to match reference CSV, got: {got}"


def test_multi_file_merge_csv_fodt_html():
    csv_str = """\
Headword,FullFormDisplay,FullFormNormalized,PartOfSpeech,NotesForeign,Meanings,NumberOfMeanings,NotesNative,MnemonicHint,PronunciationText,AudioUrl,ReferenceBook,ReferenceSection,Exercise1Front,Exercise1Back,Exercise2Front,Exercise2Back,Exercise3Front,Exercise3Back,Tags
a / ab,ā / ab,a / ab,Präposition,Präp. m. Abl.,"von, von ... her",2,,,,,Campus C1,16,,Ex1B,,,,,Top500
accipere,"accipere","accipere",Verb,,"erhalten, erfahren, annehmen",3,,,,,Campus C1,34,,,,,,,Top500
"""
    csv_reader = csv.DictReader(io.StringIO(csv_str))

    fodt_body = "<text:p><text:span>abire</text:span>    weggehen37</text:p>"
    fodt_tree = make_fodt(fodt_body)

    html_body = "<p><span>accipere, accipiō, accēpī, acceptum</span>    erhalten, erfahren, annehmen34</p>"
    html_tree = make_html(html_body)

    out = io.StringIO()
    console = FakeConsole()

    # readers: CSV file-like, FODT tree, HTML tree
    converter.convert([csv_reader, fodt_tree, html_tree], out, "Campus C1", console)

    assert (
        out.getvalue()
        == """\
Headword,FullFormDisplay,FullFormNormalized,PartOfSpeech,NotesForeign,Meanings,NumberOfMeanings,NotesNative,MnemonicHint,PronunciationText,AudioUrl,ReferenceBook,ReferenceSection,Exercise1Front,Exercise1Back,Exercise2Front,Exercise2Back,Exercise3Front,Exercise3Back,Tags
a / ab,ā / ab,a / ab,Präposition,Präp. m. Abl.,"von, von ... her",2,,,,,Campus C1,16,,Ex1B,,,,,Top500
abire,abire,abire,,,weggehen,1,,,,,Campus C1,37,,,,,,,
accipere,"accipere, accipiō, accēpī, acceptum","accipere, accipio, accepi, acceptum",Verb,,"erhalten, erfahren, annehmen",3,,,,,Campus C1,34,,,,,,,Top500
"""
    )
