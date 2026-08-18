# CONTEXT File Format

## Template of a CONTEXT file

A CONTEXT file contains a glossary as a simple definition list.

```reStructuredText
**************
{Context Name}
**************

{One or two sentence description of what this context is and why it exists.}

Order:
    {A one or two sentence description of the term}
    *Avoid*: Purchase, transaction

Invoice:
    A request for payment sent to a customer after delivery.
    *Avoid*: Bill, payment request

Customer:
    A person or organization that places orders.
    *Avoid*: Client, buyer, account
```

## Rules

- **Be opinionated.** When multiple words exist for the same concept, pick the best one and list the others under `_Avoid_`.
- **Keep definitions tight.** One or two sentences max. Define what it IS, not what it does.
- **Only include terms specific to this project's context.** General programming concepts (timeouts, error types, utility patterns) don't belong even if the project uses them extensively. Before adding a term, ask: is this a concept unique to this context, or a general programming concept? Only the former belongs.
- **Group terms under subheadings** when natural clusters emerge. If all terms belong to a single cohesive area, a flat list is fine.

## Single vs multi-context repos

**Single context (most repos):** One CONTEXT file at the repo root.

**Multiple contexts:** A CONTEXT-MAP file at the repo root lists the contexts, where they live, and how they relate to each other:

The skill infers which structure applies:

- If a CONTEXT-MAP file exists, read it to find contexts
- If only a root CONTEXT file exists, single context
- If neither exists, create a root CONTEXT file lazily when the first term is resolved

When multiple contexts exist, infer which one the current topic relates to. If unclear, ask.

## Template of a CONTEXT-MAP file

A CONTEXT-MAP file refers to all CONTEXT files of the projects as a plain list with links. And it defines the relationship between the contexts in form of a definition list.

```reStructuredText
***********
Context Map
***********

Contexts
========

- `Ordering <./src/ordering/CONTEXT.md>`__ — receives and tracks customer orders
- `Billing <./src/billing/CONTEXT.md>`__ — generates invoices and processes payments
- `Fulfillment <./src/fulfillment/CONTEXT.md>`__ — manages warehouse picking and shipping

Relationships
=============

Ordering → Fulfillment:
    Ordering emits `OrderPlaced` events; Fulfillment consumes them to start picking

Fulfillment → Billing:
    Fulfillment emits `ShipmentDispatched` events; Billing consumes them to generate invoices

Ordering ↔ Billing:
    Shared types for `CustomerId` and `Money`
```
