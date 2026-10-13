---
Title: Persitency and synchronization via Anki
Date: 2026-10-01
Status: accepted
---

******************************
Architectural Decision Records
******************************

Synchronization boundary is the Anki collection
=============================================

The in-text help workflow depends on a learner's current text unit, reading position, and deck configuration remaining consistent across Anki Desktop installations. We therefore keep those values in Anki collection data and synchronized notes/cards, rather than in plugin-owned files or a separate backend. This lets native Anki sync preserve the state without inventing a second persistence layer or a custom synchronization protocol.

The add-on itself is not synchronized
====================================

We decided that the add-on's runtime code, custom UI, and local diagnostic logs are installation-local concerns and not part of the synchronized data model. Only the durable teaching material and progress metadata live in the collection; the add-on remains separately installed on each Anki Desktop machine. This avoids accidental cross-machine drift in the program itself while keeping user content and progress portable through AnkiWeb.

Consequences
============

- User work and imported text content travel with the collection, which matches how Anki already handles deck data.
- The add-on cannot rely on plugin files to carry learner state, so all durable learning state must be represented in notes, card metadata, or collection configuration.
- The add-on needs a clear boundary between synchronized persistent state and local diagnostic/logging state to avoid confusion during support and debugging.
