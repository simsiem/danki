---
Title: Interfaces for test unit learning
Date: 2026-10-01
Status: accepted
---

******************************
Architectural Decision Records
******************************

TextLearning is the public core seam
====================================

The in-text help workflow must remain testable without Anki or Qt and must not leak collection-specific details into the learning rules. We therefore keep a single public `TextLearning` interface in the core and route deck access, reading state, vocabulary lookup, card review, and diagnostics through role-specific outbound ports. This keeps the business workflow stable while allowing the Anki Desktop adapter, the collection-backed storage layer, and the UI shell to vary independently.

Representative-card progress is the source of truth
===================================================

We decided that vocabulary progress belongs to the representative card for a vocabulary entry instead of a separate in-text review state. The core therefore asks Anki for the current schedule state, applies ratings through the scheduler, and treats the representative card as the authoritative progress record for note-level learning. This prevents duplicate state, preserves Anki's normal scheduling behavior, and avoids a second progress model that would diverge from the learner's existing review history.

Text-unit import is a versioned external contract
=================================================

Text material is not just a local convenience object; it is a durable external artifact that must be imported, synchronized, and updated predictably across machines. We therefore define the JSON representation as a strict versioned contract with `schemaVersion`, `textIdentifier`, `text`, and `vocabularyEntries`, and we reject unknown fields and unsupported legacy versions instead of silently normalizing them away. This makes re-import, deck synchronization, and future migration explicit instead of accidental.
