# Finance Dashboard Documentation

## Directory Structure

```
docs/
├── README.md                    # This file
├── versions/                    # Implementation history
│   └── v0.1/                    # v0.1 implementation details
├── diataxis/                    # User guides (Diataxis framework)
│   ├── how-to/                  # Task-oriented guides
│   └── reference/               # Technical reference
├── design_strategies/           # Architecture decision records
└── prompts/                     # AI assistant context
```

## Key Documents

| Need | Location |
|------|----------|
| Feature roadmap | `/ROADMAP.md` (project root) |
| Setup guide | `diataxis/how-to/v0.1/01-setup-environment.md` |
| Process PDFs | `diataxis/how-to/v0.1/02-process-pdf-statements.md` |
| Troubleshooting | `diataxis/how-to/v0.1/troubleshooting.md` |
| Filename format | `diataxis/reference/filename-format.md` |
| v0.1 implementation | `versions/v0.1/` |

## OpenSpec

OpenSpec specs live in `/openspec/` at the project root:
- `project.md` - Project context and conventions
- `AGENTS.md` - AI assistant instructions
- `specs/` - Archived feature specifications
- `changes/` - Active change proposals

See `/openspec/AGENTS.md` for the spec-driven development workflow.
