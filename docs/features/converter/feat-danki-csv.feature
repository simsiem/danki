Feature: Convert Campus C school-book entries

  Danki uses its own CSV based file format for a vocabulary.
  It helps to import and export vocabulary entries in Danki CLI and
  Danki plugin for Anki. Danki CLI can read and write this format.


  Scenario: Pass through Danki CSV input
    Given the CSV input:
      """
      Headword,FullFormDisplay,FullFormNormalized,PartOfSpeech,NotesForeign,Meanings,NumberOfMeanings,NotesNative,MnemonicHint,PronunciationText,AudioUrl,ReferenceBook,ReferenceSection,Exercise1Front,Exercise1Back,Exercise2Front,Exercise2Back,Exercise3Front,Exercise3Back,Tags
      -ne,-ne,-ne,,,Partikel im dir. Fragesatz (unübersetzt),1,,,,,Campus C1,13,,,,,,,Top500
      a / ab,ā / ab (m. Abl.),a / ab (m. Abl.),Präposition,Präp. m. Abl.,"von, von ... her",2,,,,,Campus C1,16,,,,,,,Top500
      abire,"abīre, abeō, abiī","abire, abeo, abii",Verb,B,weggehen,1,C,D,E,F,Campus C1,37,G,H,I,J,K,L,Top500
      Aeneas,"Aenēās, Aenēae","Aeneas, Aeneae",Nomen,m,Äneas (Trojaner und Stammvater der Römer),1,,,,,Campus C1,30,,,,,,,
      Romulus / Remus,Rōmulus / Remus,Romulus / Remus,Nomen,,Romulus / Remus,1,Zwillingsbrüder und sagenhafte Gründer Roms,,,,Campus C1,32,,,,,,,
      Tarquinius Superbus,Tarquinius Superbus,Tarquinius Superbus,Nomen,,Tarquinius Superbus,1,Letzter etruskischer König von Rom,,,,Campus C1,36,,,,,,,
      vox,"vōx, vōcis","vox, vocis",Nomen,f,"die Stimme, die Äußerung, der Laut",3,,,,,Campus C1,25,,,,,,,Top500
      """
    When Danki converts the input with book "Campus C1"
    Then the output CSV is identical to the input CSV
