import csv
import re
import unicodedata
from typing import TextIO
from xml.etree.ElementTree import Element, ElementTree

_FIELDNAMES = [
    "Headword",
    "FullFormDisplay",
    "FullFormNormalized",
    "Meanings",
    "PartOfSpeech",
    "NotesForeign",
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


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _normalize_nfkd_strip(s: str) -> str:
    if s is None:
        return ""
    nk = unicodedata.normalize("NFKD", s)
    stripped = "".join(ch for ch in nk if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", stripped).strip()


class _ElementTreeParagraphExtractor:
    def paragraphs(self, tree: ElementTree):
        root = tree.getroot()
        idx = 0
        for elem in root.iter():
            if _local_name(elem.tag).lower() == "p":
                idx += 1
                text = "".join(elem.itertext()).strip()
                yield idx, text, elem


class _StyleInspector:
    def __init__(self, tree: ElementTree):
        self.blue_classes = set()
        self._scan_styles(tree)

    def _scan_styles(self, tree: ElementTree) -> None:
        style_text = ""
        for elem in tree.getroot().iter():
            if _local_name(elem.tag).lower() == "style" and elem.text:
                style_text += elem.text + "\n"
        # find class names that set color:#0070c0
        for m in re.finditer(
            r"\.([A-Za-z0-9_-]+)\s*\{[^}]*color\s*:\s*#0070c0\b", style_text, flags=re.IGNORECASE
        ):
            self.blue_classes.add(m.group(1))

    def is_top500(self, para_elem: Element) -> bool:
        # check class attribute on paragraph
        cls = para_elem.get("class") or ""
        for c in cls.split():
            if c in self.blue_classes:
                return True
        # check inline styles inside paragraph subtree
        for e in para_elem.iter():
            st = (e.get("style") or "").lower()
            if "#0070c0" in st:
                return True
            # legacy font color
            if _local_name(e.tag).lower() == "font" and (e.get("color") or "").lower() == "#0070c0":
                return True
            # classes on child elements
            child_cls = e.get("class") or ""
            for c in child_cls.split():
                if c in self.blue_classes:
                    return True
        return False


def convert(tree: ElementTree, out_file: TextIO, book: str, console_obj) -> None:
    """Convert vocabulary from the provided ElementTree and write CSV to out_file.
    All arguments are required. Raises an exception on error."""

    extractor = _ElementTreeParagraphExtractor()
    styler = _StyleInspector(tree)

    pattern = re.compile(r"^[^\W\d_].*\s{3,}.*\d+\s*$", re.UNICODE)

    writer = csv.DictWriter(
        out_file, fieldnames=_FIELDNAMES, quoting=csv.QUOTE_MINIMAL, extrasaction="ignore"
    )
    writer.writeheader()

    seen = {}
    created = 0

    for idx, text, elem in extractor.paragraphs(tree):
        snippet_length = min(len(text), 20)
        snippet = text[: snippet_length - 1].replace("\n", " ")
        if not pattern.match(text):
            console_obj.print(f"Info: paragraph {idx} not matched: {snippet}")
            continue

        # split by first run of 3+ spaces
        parts = re.split(r"\s{3,}", text, maxsplit=1)
        if len(parts) < 2:  # noqa: PLR2004
            console_obj.print(f"Warning: paragraph {idx} unexpected format, skipping: {snippet}")
            continue
        left = parts[0].strip()
        right = parts[1].strip()

        placeholder_slash = "__SLASH__"
        placeholder_comma = "__COMMA__"
        left_parts = left.replace(" / ", placeholder_slash).replace(", ", placeholder_comma).split(maxsplit=1)
        fullform_display = left_parts[0].replace(placeholder_slash, " / ").replace(placeholder_comma, ", ")
        notes_foreign = (
            left_parts[1].replace(placeholder_slash, " / ").replace(placeholder_comma, ", ")
            if len(left_parts) > 1
            else ""
        )

        fullform_normalized = _normalize_nfkd_strip(fullform_display)
        headword = fullform_normalized.split(",")[0]

        m = re.match(r"(?s)^(?P<mean>.*?)(?P<numbers>\d+(?:[.,]\s*\d+)*)\s*$", right)
        if not m:
            console_obj.print(f"Warning: paragraph {idx} missing trailing numbers, dropping entry: {snippet}")
            continue

        meanings = m.group("mean").strip()

        numbers_raw = m.group("numbers")
        refs = re.split(r"[.,]\s*", numbers_raw)
        reference_section = ";".join(r.strip() for r in refs if r.strip())

        pos_regex_to_name = {
            re.compile(r"Präp\."): "Präposition",
            re.compile(r"Adv\."): "Adverb",
            re.compile(r"Subj\."): "Subjunktion",
            re.compile(r"^[mfn]$"): "Nomen",
            re.compile(r"[mfn]\s"): "Nomen",
            re.compile(r"m/f"): "Nomen",
        }
        for regex, pos_name in pos_regex_to_name.items():
            if regex.search(notes_foreign):
                pos = pos_name
                break
        else:
            pos = ""

        # detect Top500 tag via style inspector
        tags = []
        if styler.is_top500(elem):
            tags.append("Top500")

        # dedup by headword (exact string)
        key = headword
        row = {
            "Headword": headword,
            "FullFormDisplay": fullform_display,
            "FullFormNormalized": fullform_normalized,
            "Meanings": meanings,
            "PartOfSpeech": pos,
            "NotesForeign": notes_foreign,
            "NotesNative": "",
            "MnemonicHint": "",
            "PronunciationText": "",
            "AudioUrl": "",
            "ReferenceBook": book,
            "ReferenceSection": reference_section,
            "Exercise1Front": "",
            "Exercise1Back": "",
            "Exercise2Front": "",
            "Exercise2Back": "",
            "Exercise3Front": "",
            "Exercise3Back": "",
            "Tags": ";".join(tags),
        }

        if key in seen:
            prev = seen[key]
            # compare all fields for exact equality (trimmed)
            diffs = []
            for f in (
                "FullFormDisplay",
                "FullFormNormalized",
                "Meanings",
                "PartOfSpeech",
                "ReferenceSection",
                "NotesForeign",
                "Tags",
            ):
                a = (prev.get(f) or "").strip()
                b = (row.get(f) or "").strip()
                if a != b:
                    diffs.append((f, a, b))
            if diffs:
                msg_lines = [f"Mismatch for '{key}' in paragraph {idx}:"]
                for f, a, b in diffs:
                    msg_lines.append(f" - {f}: first='{a}' later='{b}'")
                console_obj.print("\n".join(msg_lines))
            # keep first entry
            continue

        writer.writerow(row)
        seen[key] = row
        created += 1

    console_obj.print(f"Converted {created} entries (from {len(seen)} unique headwords)")
