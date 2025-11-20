# OpenSpec Workflow Guide

A simple, end-to-end guide for using OpenSpec in this project.

## Prerequisites

- OpenSpec CLI installed: `npm install -g @fission-ai/openspec`
- Understand [OpenSpec basics](openspec_readme.md)

---

## Workflow Steps

### 1. Create a Proposal

**When:** Starting a new change (feature, refactor, documentation)

**Prompt:**
```markdown
Following #file:openspec-proposal.prompt.md, create a proposal for [CHANGE_DESCRIPTION].

Context: #file:project.md
Source: #folder:[PATH_TO_CODE]
```

**What happens:**
- AI creates `openspec/changes/[change-id]/proposal.md`
- AI creates `openspec/changes/[change-id]/tasks.md`
- AI creates `openspec/changes/[change-id]/design.md` (if needed)

**Verify:**
```bash
openspec list
```

---

### 2. Create Spec Files

**When:** After proposal is approved

**Prompt:**
```markdown
Following #file:openspec-proposal.prompt.md, create the spec file for [CHANGE_NAME].

Context: #file:project.md #file:[path/to/proposal.md]
Source: #folder:[PATH_TO_CODE]
```

**What happens:**
- AI creates `openspec/changes/[change-id]/specs/[capability]/spec.md`
- Uses delta headers: `## ADDED Requirements`, `## MODIFIED Requirements`, `## REMOVED Requirements`
- Each requirement includes `#### Scenario:` blocks

**Verify:**
```bash
openspec validate [change-id]
```

**Fix validation errors:**
- Missing delta headers: Add `## ADDED Requirements` before requirements
- Missing scenarios: Each requirement needs at least one `#### Scenario:` block
- Debug: `openspec show [change-id] --json --deltas-only`

---

### 3. Execute Tasks

**When:** Spec is validated

**Prompt:**
```markdown
Following #file:openspec-proposal.prompt.md, execute tasks from #file:[path/to/tasks.md].

Context: #file:project.md
Specs: #file:[path/to/spec.md]
Source: #folder:[PATH_TO_CODE]
```

**What happens:**
- AI implements changes according to tasks
- AI creates/modifies code files
- AI validates work against spec scenarios

**Track progress:**
```bash
openspec list
```

---

### 4. Validate & Complete

**When:** All tasks are done

**Verify:**
```bash
openspec validate [change-id] --strict
```

**Complete the change:**
```bash
openspec complete [change-id]
```

**What happens:**
- Archives change to `openspec/specs/[capability]/`
- Removes from active changes
- Preserves specs for future reference

---

## Common Patterns

### Documentation Change (No Code)

```markdown
Following #file:openspec-proposal.prompt.md, create a proposal for documenting [FEATURE_NAME].

Context: #file:project.md
Source: #folder:projects/[feature]/main/default/

Requirements:
- Document existing deployed feature
- Use discovery-based approach (analyze actual code)
- Create reference and explanation documentation only
```

### Code Feature (New Implementation)

```markdown
Following #file:openspec-proposal.prompt.md, create a proposal for implementing [FEATURE_NAME].

Context: #file:project.md
Dependencies: [list any related features]

Requirements:
- [List key requirements]
- Include test coverage
- Follow project coding standards
```

### Refactoring (Modify Existing)

```markdown
Following #file:openspec-proposal.prompt.md, create a proposal for refactoring [COMPONENT_NAME].

Context: #file:project.md
Source: #folder:[path/to/existing/code]

Goals:
- [List refactoring goals]
- Maintain backward compatibility
- Improve [performance/maintainability/etc.]
```

---

## Quick Reference

### File Structure
```
openspec/
├── project.md              # Project-wide context
├── changes/                # Active changes
│   └── [change-id]/
│       ├── proposal.md     # What and why
│       ├── tasks.md        # Ordered work items
│       ├── design.md       # Architecture (optional)
│       └── specs/
│           └── [capability]/
│               └── spec.md # Requirements & scenarios
└── specs/                  # Completed changes (archived)
    └── [capability]/
        └── spec.md
```

### Key Commands
```bash
openspec list                          # List active changes
openspec list --specs                  # List completed specs
openspec validate [change-id]          # Validate a change
openspec validate [change-id] --strict # Strict validation
openspec show [change-id]              # Show change details
openspec complete [change-id]          # Archive completed change
```

### Delta Headers (Required in spec.md)
```markdown
## ADDED Requirements        # New requirements
## MODIFIED Requirements     # Changed requirements (include full text)
## REMOVED Requirements      # Deprecated requirements
```

### Requirement Format
```markdown
### Requirement: [Name]
The system SHALL/MUST [do something].

#### Scenario: [Name]
- GIVEN [initial context]
- WHEN [action occurs]
- THEN [expected outcome]
```

---

## Troubleshooting

### Validation fails: "No deltas found"
**Fix:** Add delta header (`## ADDED Requirements`) before requirements

### Validation fails: "Requirement must include at least one Scenario"
**Fix:** Add `#### Scenario:` block to each requirement

### Can't find openspec/AGENTS.md
**Fix:** Run `openspec update` to sync OpenSpec conventions

### Change not appearing in list
**Fix:** Ensure files are in `openspec/changes/[change-id]/` directory

---

## Resources

- [OpenSpec README](openspec_readme.md) - Full OpenSpec documentation
- [Project Standards](../../openspec/project.md) - Project-specific context
- [OpenSpec Proposal Prompt](../../.github/prompts/openspec-proposal.prompt.md) - AI workflow guide
- [OpenSpec GitHub](https://github.com/Fission-AI/OpenSpec) - Official repository
