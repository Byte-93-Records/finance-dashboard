# OpenSpec vs Agentic Workflows

## Different Purposes

| Aspect | OpenSpec | Agentic Workflow |
|--------|----------|------------------|
| **Purpose** | Define *what* to build before coding | Orchestrate *how* AI executes tasks |
| **When** | Planning/spec phase | Execution phase |
| **Output** | Proposals, specs, tasks | Completed work via subagents |
| **Focus** | Human-AI alignment on requirements | Parallel task execution |

---

## Should You Combine Them?

**Yes, but at different stages:**

```
┌─────────────────────────────────────────────────────────┐
│  PLANNING (OpenSpec)                                    │
│  - Create proposal.md, spec.md, tasks.md                │
│  - Human reviews and approves                           │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  EXECUTION (Agentic Workflow)                           │
│  - Spawn subagents for parallel tasks                   │
│  - Each agent works on a spec'd task                    │
│  - Skills provide domain knowledge                      │
└─────────────────────────────────────────────────────────┘
```

---

## Practical Example

```
OpenSpec Change: v0.3-multi-source-integration
├── proposal.md    ← Human approves this
├── tasks.md       ← Becomes subagent assignments
│   ├── Task 1: Bank statement parser    → Subagent 1
│   ├── Task 2: Investment parser        → Subagent 2
│   └── Task 3: Ledger schema            → Subagent 3
└── spec.md        ← Shared context for all agents
```

---

## Recommendation

**Don't over-engineer it.** For a personal project:

1. **Keep OpenSpec light** - broad tasks, not 400 checkboxes
2. **Use subagents naturally** - when tasks are independent and parallelizable
3. **Skip the full "research agent" pattern** - unless you genuinely need persistent project context + MCP + skills + subagents

The blog example is for enterprise competitive intelligence. A finance dashboard benefits more from:
- Clear specs (OpenSpec)
- Iterative debugging
- Simple execution

---

## TL;DR

OpenSpec for planning, agentic patterns emerge naturally when you have parallelizable work. Don't force the architecture.
