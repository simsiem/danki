# AGENTS.md: Guidelines for AI Assistants

## Code Standards

### Language & Tooling

- **Language**: Python
- **Format / lint / type check / build / test**: hatch
- **Line length**: 110

### Commands for formatting and code checks

Always format and check the code (including type checks)! Use the following command:

```bash
hatch check --fix
```

This implicitely calls subcommands

```bash
hatch check fmt --fix
hatch check code --fix
hatch check types
```

### Critical Rules

- **Never call ruff directly**. Use `hatch check fmt --fix` for formatting and `hatch check code --fix` for code checks.
- **Never call pyrefly directly**. Use `hatch check types`.


## Testing Requirements

### Testing Standards

- **Always write tests** for any new code you add
- **Run tests before submitting changes** using `hatch test`

### Test Commands

Run all tests:

```bash
hatch test
```

Run all test of a certain test module, like `test_confmgmt.py` in the following example:

```bash
hatch test tests/test_confmgmt.py
```

### Critical Rules

- **Never call pytest directly**. Always use `hatch test` for testing.

## Python env for development

The hatch environment *dev* offers all dependencies and tools for debugging during development.
If missing, you can add important common tools as extra dependencies.

Enter the environment with `hatch --env dev shell`.

## Agent skills

### Issue tracker

Local Markdown issue files under `.scratch/` are used for this repo. See `docs/agents/issue-tracker.md`.

### Triage labels

The repo uses the canonical five labels: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, and `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

This is a single-context repo with a root CONTEXT file `CONTEXT.rst` and the primary ADR directory `docs/adr/` for ADRs, plus the default consumer rules for domain docs. See `docs/agents/domain.md`.

### Feature files

BDD feature files (`docs/features/**/*.feature`, executable via `pytest-bdd`) are this repo's permanent documentation. See `docs/agents/features.md`.
