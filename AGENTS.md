# AGENTS.md: Guidelines for AI Assistants

## Code Standards

### Language & Tooling

- **Language**: Python
- **Linter/Formatter**: ruff with line length of 110
- **Build/Test/Lint Manager**: hatch

### Command for linting and code formatting

```bash
hatch fmt
```

### Critical Rules

- **Never call ruff directly**. Always use `hatch fmt` for formatting.


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

## Agent skills

### Issue tracker

Local Markdown issue files under `.scratch/` are used for this repo. See `docs/agents/issue-tracker.md`.

### Triage labels

The repo uses the canonical five labels: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, and `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

This is a single-context repo with a root `CONTEXT.md` and `docs/adr/` for ADRs, plus the default consumer rules for domain docs. See `docs/agents/domain.md`.
