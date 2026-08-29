import csv
import re
import unicodedata
from typing import TextIO
from xml.etree.ElementTree import Element, ElementTree

_FIELDNAMES = [
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


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _normalize_nfkd_strip(s: str) -> str:
    if s is None:
        return ""
    nk = unicodedata.normalize("NFKD", s)
    stripped = "".join(ch for ch in nk if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", stripped).strip()


def _text_pieces_from_node(node: Element) -> list[str]:
    tag_s_full_name = "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}s"
    attrib_c_full_name = "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}c"
    if node.tag == tag_s_full_name:
        count = int(node.get(attrib_c_full_name) or "1")
        # include tail text of the <s> element (e.g. following text in the same span)
        tail = node.tail or ""
        return " " * count + tail

    pieces = []
    if node.text:
        pieces.append(node.text)
    for child in node:
        pieces.extend(_text_pieces_from_node(child))
    if node.tail:
        pieces.append(node.tail)

    return pieces


def _text_from_node(node: Element) -> str:
    return "".join(_text_pieces_from_node(node))


class _ElementTreeParagraphExtractor:
    def paragraphs(self, tree: ElementTree):
        root = tree.getroot()
        idx = 0
        for elem in root.iter():
            if _local_name(elem.tag).lower() == "p":
                idx += 1
                text = _text_from_node(elem).strip()
                yield idx, text, elem


class _StyleInspector:
    def __init__(self, tree: ElementTree):
        self.blue_classes = set()
        root_tag = tree.getroot().tag
        if root_tag == "{http://www.w3.org/1999/xhtml}html":
            self._scan_styles_element = self._scan_styles_element_html
            self._is_top500 = self._is_top500_html
        elif root_tag == "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}document":
            self._scan_styles_element = self._scan_styles_element_odt
            self._is_top500 = self._is_top500_odt
        else:
            msg = f"Unknown XML format. Root tag is {root_tag}."
            raise RuntimeError(msg)
        self._scan_styles(tree)

    def _scan_styles(self, tree: ElementTree) -> None:
        for elem in tree.getroot().iter():
            self._scan_styles_element(elem)

    def _scan_styles_element_html(self, elem: Element) -> None:
        # collect inline CSS from HTML <style> elements
        if _local_name(elem.tag).lower() == "style" and elem.text:
            for m in re.finditer(
                r"\.([A-Za-z0-9_-]+)\s*\{[^}]*color\s*:\s*#0070c0\b", elem.text, flags=re.IGNORECASE
            ):
                self.blue_classes.add(m.group(1))

    def _scan_styles_element_odt(self, elem: Element) -> None:
        # For OpenDocument style:style elements, inspect nested text-properties
        if _local_name(elem.tag).lower() == "style":
            # try to find a style name attribute (style:name)
            style_name = None
            for k, v in elem.attrib.items():
                if _local_name(k).lower() == "name":
                    style_name = v
                    break
            if style_name:
                # look for any attribute value in this style subtree that contains the target color
                found = False
                for child in elem.iter():
                    for av in child.attrib.values():
                        if isinstance(av, str) and "#0070c0" in av.lower():
                            self.blue_classes.add(style_name)
                            found = True
                            break
                    if found:
                        break

    def is_top500(self, para_elem: Element) -> bool:
        return self._is_top500(para_elem)

    def _is_top500_odt(self, para_elem: Element) -> bool:
        # check any attribute values (e.g., class names, style-name) against known blue style names
        for e in para_elem.iter():
            # check direct attribute values for a matching style-name or color
            for av in e.attrib.values():
                if not av:
                    continue
                # direct style-name reference (e.g. text:style-name -> 'T11')
                if av in self.blue_classes:
                    return True
                # inline color attributes (e.g. fo:color) or inline CSS fragments
                if isinstance(av, str) and "#0070c0" in av.lower():
                    return True
        return False

    def _is_top500_html(self, para_elem: Element) -> bool:
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


def _first_span_text(elem: Element) -> str:
    for e in elem.iter():
        if _local_name(e.tag).lower() == "span":
            return "".join(e.itertext()).strip()
    msg = 'Element {elem} does not contain a "<span>" element.'
    raise ValueError(msg)


def _extract_full_form_display(paragraph_element: Element, _plain_text: str) -> str:
    result = ""
    pieces = _text_pieces_from_node(paragraph_element)

    for p in pieces:
        if len(result) >= 2 and (  # noqa: PLR2004
            (result[-1] == " " and result[-2] not in ("/", ","))
            or (p[0] == " " and result[-1] not in ("/", ","))
        ):
            return result.strip()
        result += p

    msg = f"Could not find full_form_display in {pieces}."
    raise ValueError(msg)


def _snippet(text: str) -> str:
    if len(text) == 0:
        return ""
    snippet_length = min(len(text), 60)
    return text[:snippet_length].replace("\n", " ")


def _compress_full_form_display(s: str) -> str:
    """If `s` contains three comma-separated forms that share a common
    prefix and the suffixes are exactly 'us', 'a', 'um', compress them to
    the form: <fullfirst>, <second-suffix>, <third-suffix>.
    Example: "beātus, beāta, beātum" -> "beātus, a, um".
    """
    parts = [p.strip() for p in s.split(",")]
    if len(parts) != 3:  # noqa: PLR2004
        return s.strip()

    a, b, c = parts

    sa = "us"
    if len(a) > len(sa) and a[-2:] == sa and b == a[:-2] + "a" and c == a[:-2] + "um":
        return f"{a}, a, um"

    return s.strip()


def _part_of_speech_from_notes_foreign(notes_foreign) -> str:
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
            return pos_name
    return ""


def _format_mismatch(field: str, info: str) -> str:
    return f"WARNING: Mismatch for {field} - {info}."


def _format_merge(field: str, info: str) -> str:
    return f"INFO: Merge {field} - {info}."


def _split_to_int_set(text: str, sep: str) -> set[int]:
    return {int(part) for part in text.split(sep)}


def _merge_non_empty(field, previous, later) -> tuple[str | None, str]:
    if previous == later:
        return None, previous
    if previous == "":
        msg = _format_merge(field, f'previous = "", chosen = "{later}"')
        return msg, later
    if later == "":
        msg = _format_merge(field, f'later = "", chosen = "{previous}"')
        return msg, previous
    msg = _format_mismatch(field, f'previous = "{previous}", later = "{later}"')
    return msg, previous


def _merge_exact_match(field, previous: str, later: str) -> tuple[str | None, str]:
    if previous == later:
        return None, previous
    msg = _format_mismatch(field, f'previous = "{previous}", later = "{later}"')
    return msg, previous


def _merge_sets(field, previous: set[int], later: set[int]) -> tuple[str | None, set[int]]:
    if previous == later:
        return None, previous

    if previous.issubset(later):
        msg = _format_merge(field, f'previous = "{previous}", chosen = "{later}"')
        return msg, later
    if later.issubset(previous):
        msg = _format_merge(field, f'later = "{later}", chosen = "{previous}"')
        return msg, previous

    msg = _format_mismatch(field, f'previous = "{previous}", later = "{later}"')
    return msg, previous


def _merge_full_form_display(previous, later) -> tuple[str | None, str]:
    if previous == later:
        return None, previous

    previous_parts = [part.strip() for part in previous.split(",")]
    later_parts = [part.strip() for part in later.split(",")]

    common_range = min(len(previous_parts), len(later_parts))
    if all(previous_parts[i] == later_parts[i] for i in range(common_range)):
        if len(later_parts) > len(previous_parts):
            msg = _format_merge("FullFormDisplay", f'previous = "{previous}", chosen = "{later}"')
            return msg, later
        msg = _format_merge("FullFormDisplay", f'later = "{later}", chosen = "{previous}"')
        return msg, previous
    msg = _format_mismatch("FullFormDisplay", f'previous = "{previous}", later = "{later}"')
    return msg, previous


def convert(tree: ElementTree, out_file: TextIO, book: str, console_obj) -> None:
    """Convert vocabulary from the provided ElementTree and write CSV to out_file.
    All arguments are required. Raises an exception on error."""

    extractor = _ElementTreeParagraphExtractor()
    styler = _StyleInspector(tree)
    vocabulary_paragraph_pattern = re.compile(r"^[\S].*\s{3,}.*\d+\s*$", re.UNICODE)
    writer = csv.DictWriter(
        out_file, fieldnames=_FIELDNAMES, quoting=csv.QUOTE_MINIMAL, extrasaction="ignore"
    )
    writer.writeheader()

    vocabulary_list = {}

    for idx, text, elem in extractor.paragraphs(tree):
        #
        # Identify paragraph with a vocabulary entry
        #
        if len(text) == 0 or text[0] == "#":
            continue
        if not vocabulary_paragraph_pattern.match(text):
            console_obj.print(f"WARNING: Paragraph {idx} not matched: {_snippet(text)}")
            continue

        #
        # Extract fields from paragraph
        #

        # split by last run of 3+ spaces
        m = re.search(r"\s{3,}(?!.*\s{3,})", text)
        if not m:
            console_obj.print(f"Warning: paragraph {idx} unexpected format, skipping: {_snippet(text)}")
            continue
        left = text[: m.start()].strip()
        right = text[m.end() :].strip()

        pre_full_form_display = _extract_full_form_display(elem, text)
        extracted_full_form_display = _compress_full_form_display(pre_full_form_display)
        headword = _normalize_nfkd_strip(extracted_full_form_display.split(",")[0])
        extracted_notes_foreign = left[len(pre_full_form_display) :].strip()

        m = re.match(r"(?s)^(?P<mean>.*?)(?P<numbers>\d+(?:[.,]\s*\d+)*)\s*$", right)
        if not m:
            console_obj.print(
                f"Warning: paragraph {idx} missing trailing numbers, dropping entry: {_snippet(text)}"
            )
            continue

        extracted_meanings = m.group("mean").strip()

        numbers_raw = m.group("numbers")
        refs = re.split(r"[.,]\s*", numbers_raw)
        extracted_reference_sections = {int(r.strip()) for r in refs if r.strip()}

        # detect Top500 tag via style inspector
        extracted_tags = []
        if styler.is_top500(elem):
            extracted_tags.append("Top500")

        #
        # Merge extracted fields with previous entry if available
        #

        if headword in vocabulary_list:
            messages = []
            prev = vocabulary_list[headword]

            msg, new_full_form_display = _merge_full_form_display(
                prev["FullFormDisplay"], extracted_full_form_display
            )
            if msg:
                messages.append(msg)

            msg, new_notes_foreign = _merge_non_empty(
                "NotesForeign", prev["NotesForeign"], extracted_notes_foreign
            )
            if msg:
                messages.append(msg)

            msg, new_meanings = _merge_exact_match("Meanings", prev["Meanings"], extracted_meanings)
            if msg:
                messages.append(msg)

            msg, new_reference_section = _merge_sets(
                "ReferenceSection",
                _split_to_int_set(prev["ReferenceSection"], ";"),
                extracted_reference_sections,
            )
            if msg:
                messages.append(msg)

            extracted_tags_string = ";".join(extracted_tags)
            msg, new_tags = _merge_non_empty("Tags", prev["Tags"], extracted_tags_string)
            if msg:
                messages.append(msg)

            with_info_messages = True
            print_logs = len(messages) > 0 if with_info_messages else any("WARNING" in m for m in messages)
            if print_logs:
                console_obj.print(f'Changes for "{headword}" in paragraph {idx}:')
                for msg in messages:
                    console_obj.print("- " + msg)

        else:
            new_full_form_display = extracted_full_form_display
            new_notes_foreign = extracted_notes_foreign
            new_meanings = extracted_meanings
            new_reference_section = extracted_reference_sections
            new_tags = ";".join(extracted_tags)

        #
        # Update vocabulary list
        #
        vocabulary_list[headword] = {
            "Headword": headword,
            "FullFormDisplay": new_full_form_display,
            "FullFormNormalized": _normalize_nfkd_strip(new_full_form_display),
            "PartOfSpeech": _part_of_speech_from_notes_foreign(new_notes_foreign),
            "NotesForeign": new_notes_foreign,
            "Meanings": new_meanings,
            "NumberOfMeanings": new_meanings.count(",") + new_meanings.count(";") + 1,
            "NotesNative": "",
            "MnemonicHint": "",
            "PronunciationText": "",
            "AudioUrl": "",
            "ReferenceBook": book,
            "ReferenceSection": ";".join(map(str, sorted(new_reference_section))),
            "Exercise1Front": "",
            "Exercise1Back": "",
            "Exercise2Front": "",
            "Exercise2Back": "",
            "Exercise3Front": "",
            "Exercise3Back": "",
            "Tags": new_tags,
        }

    for row in vocabulary_list.values():
        writer.writerow(row)

    created = len(vocabulary_list)
    console_obj.print(f"Converted {created} entries.")
