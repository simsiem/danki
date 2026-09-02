Merge files
===========

User stories
------------

1. As a user, I want Danki CLI to process several input files so that I can merge several files that were
   published for the same book series in one Anki deck.
2. As a user, I want Danki CLI to process several input files so that I can iteratively work on the input data
   and the resulting CSV file in cycles.


Functional acceptance criteria
------------------------------

Danki CLI shall read several input files file-by-file into the same vocabulary entry list. It shall merge them
according to the rules in `docs/design/dsgn-vocabulary-entry-merging.rst` and output the resulting list in one
CSV output file, as if all input data would be in one file.

1. When the user runs ``danki convert --help``,
   the output shows that Danki CLI accepts several input files as an arbitrary length sequence of positional arguments on
   the command line (like ``danki convert --book --output-file output.csv "Campus C" file1.csv file2.fodt file3.fodt``).

2. When the user specifies one input file *file1.csv* that is a previous output of Danki CLI,
   Danki CLI outputs one file *output.csv* that is the same as *file1.csv*.

3. When the user specifies the input files *file1.csv*, *file2.fodt* and *file3.fodt* on the command line,
   Danki CLI outputs one file that matches *output.csv*.


Non-functional acceptance criteria
----------------------------------

None
