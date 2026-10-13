# ruff: noqa: INP001, T201
"""Check a lemmatized text JSON against its vocabulary CSV."""

import csv
import json
import re
import sys


def main(json_path: str, csv_path: str) -> int:
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    with open(csv_path, encoding="utf-8") as f:
        headwords = {row["Headword"] for row in csv.DictReader(f)}

    errors = 0
    entries = data.get("vocabularyEntries")
    if not isinstance(entries, list):
        print("invalid vocabularyEntries: expected an array")
        entries = []
        errors += 1
    forms = []

    for index, e in enumerate(entries):
        if not isinstance(e, dict):
            print(f"invalid entry: vocabularyEntries[{index}] must be an object")
            errors += 1
            continue
        surface_form = e.get("surfaceForm")
        if not isinstance(surface_form, str) or not surface_form.strip():
            print(f"invalid entry: vocabularyEntries[{index}] must have a non-empty string 'surfaceForm'")
            errors += 1
            continue
        forms.append(surface_form)

        unknown_fields = set(e) - {"surfaceForm", "headwords", "notes"}
        if unknown_fields:
            print(
                f"invalid entry fields: {surface_form} contains unknown fields: {', '.join(sorted(unknown_fields))}"
            )
            errors += 1
        has_headwords = "headwords" in e
        has_notes = "notes" in e
        if has_headwords == has_notes:
            sys.stdout.write(
                f"invalid entry fields: {surface_form} must contain exactly one of 'headwords' or 'notes'\n"
            )
            errors += 1
            continue
        if has_headwords and (
            not isinstance(e["headwords"], list)
            or not all(isinstance(headword, str) and headword for headword in e["headwords"])
        ):
            print(f"invalid entry fields: {surface_form} 'headwords' must be an array of non-empty strings")
            errors += 1
            continue
        if has_notes and not isinstance(e["notes"], str):
            print(f"invalid entry fields: {surface_form} 'notes' must be a string")
            errors += 1
            continue
        if has_headwords:
            for h in e["headwords"]:
                if h not in headwords:
                    print(f"missing headword: {surface_form} -> {h}")
                    errors += 1
    if forms != sorted(forms, key=str.lower):
        print("unsorted: vocabularyEntries not sorted case-insensitively")
        errors += 1
    lowered = [f.lower() for f in forms]
    for dup in sorted({f for f in lowered if lowered.count(f) > 1}):
        print(f"duplicate: {dup}")
        errors += 1

    tokens = {re.sub(r"\d", "", t) for t in re.findall(r"[^\W\d_]+\d*", data["text"])}
    known = set(lowered)
    uncovered = sorted({t for t in tokens if t.lower() not in known}, key=str.lower)
    extra = sorted(f for f in known if f not in {t.lower() for t in tokens})
    print("uncovered (must all be German):", " ".join(uncovered))
    for f in extra:
        print(f"extra: {f} not in text")
        errors += 1

    print("errors:", errors)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
