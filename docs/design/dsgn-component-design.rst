Component design
================

Danki shall follow hexagonal architecture principles with injectable objects to the business logic so it is
easier to maintain and to extend in the future.

Design decisions
----------------

Provide a single, well-typed converter function as the primary seam:

    convert(tree: ElementTree, out_file: TextIO, book: str, console: Console) -> None

This function implements the agreed parsing rules, normalization, duplicate detection, tagging, and CSV
export. `cli.py` wires to this function. Tests exercise `convert()` directly by supplying an `ElementTree` and
an in-memory `TextIO`.

Error handling: `converter.py` reports errors as exceptions. The module `cli.py` prints them and results in
exit code `1`.


Testing decisions
-----------------

- Module tests of `converter.py` shall run without console and filesystem access. They shall mock both.
