## Different Purposes

| Aspect | OpenSpec | Execution Tools (Skills, Subagents, Direct) |
|--------|----------|---------------------------------------------|
| **Purpose** | Define *what* to build before coding | Orchestrate *how* AI executes tasks |
| **When** | Planning/spec phase | Execution phase |
| **Output** | Proposals, specs, tasks | Completed work |
| **Focus** | Human-AI alignment on requirements | Task completion via appropriate method |

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
│  EXECUTION (Choose Approach)                            │
│                                                         │
│  Direct Execution ────► Simple, sequential tasks        │
│  Skills ──────────────► Reusable procedural knowledge   │
│  Subagents ───────────► Parallel, independent tasks     │
│                                                         │
│  Often combined: Subagent uses Skill for domain logic   │
└─────────────────────────────────────────────────────────┘
```

---

## Execution Approaches Explained

### Direct Execution
Claude works through tasks sequentially using tools directly.

**When to use:**
- Simple, linear tasks
- Single-file changes
- Quick iterations

**Example:**
```
Task: Add logging to router.py
→ Claude reads file, edits directly, done
```

### Skills
On-demand procedural knowledge loaded when relevant.

**When to use:**
- Reusable expertise across conversations/projects
- Domain-specific patterns (security reviews, PDF parsing)
- Organizational workflows (commit formats, doc templates)

**Example:**
```
Task: Review code for OWASP vulnerabilities
→ Claude loads "security-review" skill
→ Applies OWASP checklist to code
```

### Subagents (Agentic Workflows)
Spawn independent agents for parallel work with isolated contexts.

**When to use:**
- Tasks are independent and parallelizable
- Complex multi-step work requiring focused context
- Research + implementation happening concurrently

**Example:**
```
Task: Implement 3 PDF processors simultaneously
→ Subagent 1: AmexProcessor (uses "pdf-parsing" skill)
→ Subagent 2: ChaseProcessor (uses "pdf-parsing" skill)
→ Subagent 3: CitiProcessor (uses "pdf-parsing" skill)
→ All work in parallel
```

---

## Practical Example: OpenSpec + Execution

```
OpenSpec Change: v0.2-pdf-processors
├── proposal.md    ← Human approves this
├── tasks.md       ← Determines execution approach
│   ├── Task 1: Create base.py           → Direct (simple)
│   ├── Task 2: Implement AmexProcessor  → Subagent + "pdf-parsing" skill
│   ├── Task 3: Implement ChaseProcessor → Subagent + "pdf-parsing" skill
│   └── Task 4: Update router.py         → Direct (simple)
└── spec.md        ← Shared context for all execution methods
```

**Why this mix?**
- Tasks 2 & 3 are parallelizable → subagents
- Both use same domain logic → skill provides "pdf-parsing" expertise
- Tasks 1 & 4 are sequential setup/glue → direct execution

---

## When to Use Each Execution Method

| Method | Independent Tasks | Reusable Logic | Parallel Work | Complexity |
|--------|-------------------|----------------|---------------|------------|
| **Direct** | Not needed | Not needed | No | Low |
| **Skills** | Optional | Yes | Optional | Medium |
| **Subagents** | Yes | Optional | Yes | High |

**Decision tree:**
1. Is the task repeatable across projects? → **Skill**
2. Can tasks run in parallel? → **Subagents** (may use Skills)
3. Otherwise → **Direct execution**

---

## Recommendation

**Don't over-engineer it.** For a personal project:

1. **Start with OpenSpec** - clear specs, broad tasks
2. **Default to direct execution** - simplest approach
3. **Use skills for domain expertise** - security, parsing, formatting patterns
4. **Use subagents when parallelism helps** - independent modules, research + build
5. **Skills + subagents together** - when parallel tasks need shared expertise

**Example progression:**
- v0.1: Direct execution (MVP, learning codebase)
- v0.2: Skills for PDF parsing (repeated logic across processors)
- v0.2: Subagents for parallel processor implementation (5 banks at once)

---

## TL;DR

- **OpenSpec** = Planning (what to build)
- **Direct** = Simple execution (sequential tasks)
- **Skills** = Procedural knowledge (reusable expertise)
- **Subagents** = Parallel execution (independent tasks)

Use OpenSpec for planning, pick execution method by task characteristics. Don't force complexity.
