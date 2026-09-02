Merging duplicate entries
-------------------------

For two entries of the same headword, some fields can be merged.

`FullFormDisplay`:
    For a comma-separated multi-part entry, choose the value with more parts, if the common parts between both
    match exactly. Example:

        <p><span>audīre, audiō</span>    hören, lernen32</p>
        <p><span>audīre, audiō, audīvī, audītum</span>    hören, lernen32</p>
    
    Results in

        'audire,"audīre, audiō, audīvī, audītum","audire, audio, audivi, auditum",,,"hören, lernen",2,,,,,book1,32,,,,,,,',

`NotesForeign`:
    If this field is empty in one entry but not in the other one, choose the non-empty value.

`Meanings`:
    This field must match exactly in both entries. No further merging rules.

`ReferenceSection`:
    Consider the referenced sections as a set of integers. Take the larger set if the smaller set is a subset.
    Otherwise report a mismatch.

`Tags`:
    If this field is empty in one entry but not in the other one, choose the non-empty value.

`FullFormNormalized` and `PartOfSpeech` are derived from the above merged values as described in the previous
section.
