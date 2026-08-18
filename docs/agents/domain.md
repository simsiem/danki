# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## File format and file names

The domain documentation files are written in reStructuredText with the file name extension `.rst`. Their file names are:

- **CONTEXT file**: `CONTEXT.rst`
- **CONTEXT-MAP file**: `CONTEXT-MAP.rst`
- **ADR**: `docs/adr/*.rst` and, in a multi-context repo, `src/<context>/docs/adr/*.rst`.

Consequently, the **ADR directories** are

- the **primary ADR directory**: `docs/adr/` and
- the **context ADR directories**: `src/<context>/docs/adr/`.

## Before exploring, read these

- **the CONTEXT file** at the repo root, or
- **a CONTEXT-MAP file** at the repo root if it exists — it points at one CONTEXT file per context. Read each one relevant to the topic.
- **the primary ADR directory** — read ADRs that touch the area you're about to work in. In multi-context repos, also check **context ADR directory** for context-scoped decisions.

If any of these files don't exist, **proceed silently**. Don't flag their absence; don't suggest creating them upfront. The `/domain-modeling` skill (reached via `/grill-with-docs` and `/improve-codebase-architecture`) creates them lazily when terms or decisions actually get resolved.

## File structure

Single-context repo (most repos):

```
/
├── CONTEXT.rst
├── docs/adr/
│   ├── 0001-event-sourced-orders.rst
│   └── 0002-postgres-for-write-model.rst
└── src/
```

Multi-context repo (presence of a CONTEXT-MAP file at the root):

```
/
├── CONTEXT-MAP.rst
├── docs/adr/                          ← system-wide decisions
└── src/
    ├── ordering/
    │   ├── CONTEXT.rst
    │   └── docs/adr/                  ← context-specific decisions
    └── billing/
        ├── CONTEXT.rst
        └── docs/adr/
```

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis, a test name), use the term as defined in the CONTEXT file. Don't drift to synonyms the glossary explicitly avoids.

If the concept you need isn't in the glossary yet, that's a signal — either you're inventing language the project doesn't use (reconsider) or there's a real gap (note it for `/domain-modeling`).

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR-0007 (event-sourced orders) — but worth reopening because…_
