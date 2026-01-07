# AI-Assisted Development Process & Checklist

A reference guide for using Claude Code with OpenSpec to manage feature development.

---

## 📁 Metadata: Key Reference Files

### Generic Files (OpenSpec-Compatible Projects)

**Core Documentation:**
- **CHANGELOG.md** - Track all changes using Keep a Changelog format + Semantic Versioning
- **ROADMAP.md** - High-level feature roadmap and release themes
- **README.md** - Project overview, setup instructions, usage
- **AGENTS.md** - AI workflow instructions (auto-managed by OpenSpec)

**OpenSpec Structure:**
- **openspec/project.md** - Project conventions, architecture, code style
- **openspec/changes/{feature}/** - Change proposals (before implementation)
  - `proposal.md` - Why and what changes
  - `spec.md` - Detailed specifications with requirements and scenarios
  - `tasks.md` - Implementation checklist
  - `design.md` - Technical decisions (optional)
- **openspec/specs/** - Finalized specifications (after archiving changes)
- **openspec/{VERSION}_OVERVIEW.md** - Release overview with feature matrix (e.g., V0.2_OVERVIEW.md)

### Project-Specific Files (Finance Dashboard)

**Project Context:**
- **TOOLS.md** - Source of truth for all tool versions, dependencies, installation instructions

**Infrastructure & Configuration:**
- **pyproject.toml** - Python dependencies and project metadata
- **docker-compose.yml** - Service definitions (Python, PostgreSQL, Grafana)
- **Dockerfile** - Container build with system dependencies
- **.env.example** - Environment variable template (checked into git)
- **.env** - Runtime secrets (NOT in git)
- **alembic.ini** - Database migration configuration

**Application Code:**
- **database/models.py** - SQLAlchemy ORM models
- **database/alembic/versions/** - Database migration scripts
- **pdf_processor/** - PDF extraction module
  - `processors/` - Bank-specific extraction logic
  - `router.py` - Route PDFs to appropriate processor
  - `cli.py` - CLI entry point
- **scripts/ingestion/** - Data ingestion workflows
- **scripts/analytics/** - Data analysis and reporting
- **grafana/dashboards/** - Dashboard JSON definitions

---

## 🔄 Generic Process: OpenSpec-Based Development

This process applies to ANY project using OpenSpec, regardless of tech stack.

### Phase 1: Planning (Spec-Driven)

**Step 1: Read existing context**
- [ ] Review ROADMAP.md for current release theme
- [ ] Review openspec/project.md for project conventions
- [ ] Understand current feature scope from openspec/{VERSION}_OVERVIEW.md

**Step 2: Create OpenSpec change proposal**
- [ ] Ask Claude: "Create an OpenSpec proposal for [feature name]"
- [ ] AI scaffolds: `openspec/changes/{feature}/proposal.md`, `spec.md`, `tasks.md`
- [ ] Review proposal: does it match your intent?

**Step 3: Refine specs until aligned** (feedback loop)
- [ ] Ask: "Can you add acceptance criteria for [scenario]?"
- [ ] Ask: "Should we handle [edge case]? If yes, add a spec"
- [ ] Ask: "Does this reference all required tools?"
- [ ] Iterate until spec captures complete requirements

**Step 4: Validate proposal against project constraints**
- [ ] Does it follow openspec/project.md conventions?
- [ ] Does it fit ROADMAP.md timeline/theme?
- [ ] Are all dependencies documented?
- [ ] No unexpected scope creep?

### Phase 2: Implementation (Task-Driven)

**Step 5: Choose execution approach**

Review tasks.md and decide execution method(s):

| Method | When to Use | Example |
|--------|-------------|---------|
| **Direct** | Simple, sequential tasks | Single file edits, config changes |
| **Skills** | Reusable domain expertise | Security reviews, PDF parsing patterns |
| **Subagents** | Parallel, independent tasks | Multiple processors, research + build |

**Decision tree:**
1. Is the task repeatable across projects? → **Skill**
2. Can tasks run in parallel? → **Subagents** (may use Skills)
3. Otherwise → **Direct execution**

**Step 6: Start implementation**
- [ ] Ask: "The specs look good. Let's implement this change"
- [ ] For direct: Claude uses `/openspec:apply {feature}` or "implement the tasks"
- [ ] For skills: "Use the {skill-name} skill to implement {task}"
- [ ] For subagents: "Spawn subagents for tasks 2-4 in parallel"
- [ ] AI follows tasks.md checklist with chosen execution method(s)

**Step 7: Track progress during implementation**
- [ ] Each task marked complete as finished
- [ ] Watch for spec deviations (ask to realign if needed)
- [ ] Verify tool usage matches documentation
- [ ] Monitor subagent progress if running in parallel

**Step 8: Handle blockers & iterations**
- [ ] If a task hits an issue: describe the problem clearly
- [ ] Ask: "Can you adjust the approach to handle [constraint]?"
- [ ] Update tasks.md if scope changes (get approval first)
- [ ] Don't let implementation drift from spec

### Phase 3: Finalization (Audit & Archive)

**Step 9: Verify implementation complete**
- [ ] All tasks marked complete
- [ ] No spec deviations unresolved
- [ ] Code follows project conventions (openspec/project.md)
- [ ] Documentation updated (CHANGELOG.md, README.md)

**Step 10: Archive the change** (merge specs into source of truth)
- [ ] Ask: "Please archive the {feature} change"
- [ ] Claude runs: `openspec archive {feature} --yes`
- [ ] Specs move: `openspec/changes/` → `openspec/specs/`
- [ ] Automatic cleanup of change folder

**Step 11: Update project documentation**
- [ ] CHANGELOG.md updated with feature + date
- [ ] ROADMAP.md updated (move to completed section)
- [ ] openspec/project.md updated if conventions changed
- [ ] README.md updated if user-facing

---

## 🎯 Project-Specific Process: Finance Dashboard

This process is specific to the Finance Dashboard project architecture and tech stack.

### Before Starting Any Feature

**Health Checks:**
```bash
# View active OpenSpec changes
openspec list

# Check git branch and status
git status

# Verify Docker services healthy
docker compose ps
```

**Understand the Codebase:**
```
finance-dashboard/
├── TOOLS.md                           ← Dependencies & versions
├── ROADMAP.md                         ← Release themes
├── CHANGELOG.md                       ← What's been done
├── openspec/
│   ├── V0.2_OVERVIEW.md              ← Current release
│   ├── project.md                    ← Conventions
│   ├── changes/v0.2-**/              ← Active proposals
│   └── specs/                        ← Finalized specs
├── database/
│   ├── models.py                     ← SQLAlchemy ORM
│   └── alembic/versions/             ← Migrations
├── pdf_processor/
│   ├── processors/                   ← Bank extractors
│   ├── router.py                     ← PDF routing
│   └── cli.py                        ← CLI entry
├── pyproject.toml                    ← Python deps
└── docker-compose.yml                ← Services
```

### Project-Specific Execution Examples

**v0.2-pdf-processors (Mixed Execution):**
```
Tasks breakdown:
- Task 1: Create base.py           → Direct (simple setup)
- Task 2: Implement AmexProcessor  → Subagent + "pdf-parsing" skill
- Task 3: Implement ChaseProcessor → Subagent + "pdf-parsing" skill
- Task 4: Update router.py         → Direct (simple glue code)

Why this mix?
- Tasks 2 & 3 are parallelizable → subagents
- Both use same domain logic → skill provides "pdf-parsing" expertise
- Tasks 1 & 4 are sequential → direct execution
```

**v0.2-data-architecture (Direct + Skill):**
```
Tasks breakdown:
- All Alembic migrations → Direct (sequential schema changes)
- Use "database-migration" skill → Ensures proper upgrade()/downgrade() patterns
```

### Project-Specific Validation Steps

**Before Implementation:**
- [ ] Read TOOLS.md version requirements for feature
- [ ] Check if database changes needed (→ Alembic migration required)
- [ ] Check if new Python dependency needed (→ update pyproject.toml)
- [ ] Check if Docker changes needed (→ update Dockerfile, docker-compose.yml)
- [ ] Verify feature aligns with current release theme (e.g., v0.2: Scale & Reliability)
- [ ] Decide execution approach based on task characteristics

**During Implementation:**
- [ ] Type hints required for all function signatures
- [ ] Google-style docstrings for public functions
- [ ] Follow PEP 8 (Black formatter: 88 char lines)
- [ ] No hardcoded values (use environment variables)
- [ ] Database: Use SQLAlchemy ORM (no raw SQL)
- [ ] Database: Create Alembic migration (not direct schema changes)
- [ ] Database: Use NUMERIC for financial amounts (never float)
- [ ] CLI changes: Use Click decorators
- [ ] PDF processors: Test all 4 types (Amex, Chase, Citi, Generic)
- [ ] Docker changes: Test with `docker compose up --build`
- [ ] Logging: Use structlog for structured output

**After Implementation:**
- [ ] Test with real data: place PDFs in `data/pdfs/`, run `./scripts/process-and-view.sh`
- [ ] Verify deduplication: Re-import same PDF shouldn't create duplicates (SHA-256 hash)
- [ ] Check Grafana: Dashboards load at http://localhost:3000
- [ ] Update TOOLS.md if new tool/version added
- [ ] Update CHANGELOG.md with changes + date
- [ ] Update ROADMAP.md if moving feature status

### v0.2 Feature Implementation Order

These features have dependencies. **Implement in this order:**

1. **v0.2-data-architecture** ← Foundation (do first)
   - Execution: Direct (sequential migrations)
   - Tools: SQLAlchemy, Alembic, PostgreSQL
   - Output: Database migrations, new models

2. **v0.2-database-performance** ← After data architecture
   - Execution: Direct (sequential index creation)
   - Tools: SQLAlchemy, Alembic, PostgreSQL
   - Output: Index migrations

3. **v0.2-pdf-processors** ← Can run parallel with above
   - Execution: Mixed (Direct + Subagents + Skills)
   - Tools: pdfplumber, Docling, Click
   - Output: processors/, router.py

4. **v0.2-bulk-processing** ← After pdf-processors stable
   - Execution: Direct (single feature, sequential)
   - Tools: Click, structlog, Python concurrent.futures
   - Output: bulk_processor.py, CLI flags

5. **v0.2-dashboard-improvements** ← Last (uses all other features)
   - Execution: Direct (Grafana config changes)
   - Tools: Grafana, PostgreSQL
   - Output: Dashboard JSON, views

---

## 🛠️ Execution Approaches Explained

### Direct Execution
Claude works through tasks sequentially using tools directly.

**When to use:**
- Simple, linear tasks
- Single-file changes
- Sequential operations (database migrations)
- Quick iterations

**Example:**
```
Task: Add logging to router.py
→ Ask: "Add debug logging to router.py"
→ Claude reads file, edits directly, done
```

### Skills (On-Demand Procedural Knowledge)
Portable expertise that loads when relevant (progressive disclosure).

**When to use:**
- Reusable expertise across conversations/projects
- Domain-specific patterns (security reviews, PDF parsing, database migrations)
- Organizational workflows (commit formats, doc templates)
- Complex procedural knowledge (OWASP checklists, financial calculations)

**Example:**
```
Task: Review code for OWASP vulnerabilities
→ Ask: "Use the security-review skill to check for vulnerabilities"
→ Claude loads "security-review" skill
→ Applies OWASP checklist to code
```

**Creating Skills:**
- Create reusable skills for repeated patterns in your project
- Example: "pdf-parsing" skill for Finance Dashboard bank statement logic
- Example: "database-migration" skill for Alembic best practices

### Subagents (Parallel Task Delegation)
Spawn independent agents for concurrent work with isolated contexts.

**When to use:**
- Tasks are independent and parallelizable
- Complex multi-step work requiring focused context
- Research + implementation happening concurrently
- Multiple similar modules (e.g., 5 bank processors)

**Example:**
```
Task: Implement 3 PDF processors simultaneously
→ Ask: "Spawn subagents to implement Amex, Chase, Citi processors in parallel"
→ Subagent 1: AmexProcessor (uses "pdf-parsing" skill)
→ Subagent 2: ChaseProcessor (uses "pdf-parsing" skill)
→ Subagent 3: CitiProcessor (uses "pdf-parsing" skill)
→ All work concurrently
```

### Combining Approaches

**Best practice: Mix execution methods based on task characteristics**

```
Example: v0.2-pdf-processors
├── Task 1: Create base.py           → Direct (setup)
├── Task 2: Implement AmexProcessor  → Subagent + "pdf-parsing" skill
├── Task 3: Implement ChaseProcessor → Subagent + "pdf-parsing" skill
├── Task 4: Implement CitiProcessor  → Subagent + "pdf-parsing" skill
└── Task 5: Update router.py         → Direct (glue code)

Rationale:
- Tasks 2-4: Parallelizable → subagents for speed
- Tasks 2-4: Shared logic → skill provides PDF parsing patterns
- Tasks 1, 5: Sequential → direct execution
```

---

## ✅ Generic Checklist: Feature Implementation

Use this for ANY OpenSpec-managed feature, regardless of project.

### Pre-Implementation
- [ ] OpenSpec proposal created & approved
- [ ] Specs reviewed and aligned with requirements
- [ ] tasks.md complete and realistic
- [ ] Tool requirements documented
- [ ] No unexpected dependencies introduced
- [ ] Execution approach selected for each task (Direct/Skills/Subagents)

### Code Implementation
- [ ] All tasks completed from tasks.md
- [ ] Code follows project conventions (see openspec/project.md)
- [ ] No hardcoded values (use configuration)
- [ ] Logging implemented appropriately
- [ ] Error handling in place
- [ ] Appropriate execution method used for each task

### Testing & Validation
- [ ] Functionality tested manually or automated
- [ ] No regressions in existing features
- [ ] Edge cases handled

### Documentation & Versioning
- [ ] CHANGELOG.md updated (what + date)
- [ ] ROADMAP.md updated (if moving feature status)
- [ ] openspec/project.md updated if conventions changed
- [ ] README.md updated if user-facing change
- [ ] Git commits follow conventional commits (`feat:`, `fix:`, `docs:`, `refactor:`)

### OpenSpec Finalization
- [ ] Run: `openspec archive {feature} --yes`
- [ ] Verify: specs moved to `openspec/specs/`
- [ ] Verify: change folder cleaned up
- [ ] Commit: `git add openspec/ && git commit -m "docs: archive {feature}"`

---

## ✅ Project-Specific Checklist: Finance Dashboard

Use this for Finance Dashboard features specifically.

### Database Changes
- [ ] Alembic migration created (not direct schema changes)
- [ ] Migration includes both `upgrade()` and `downgrade()`
- [ ] Migration tested: can apply and rollback cleanly
- [ ] Models updated in `database/models.py`
- [ ] Use NUMERIC for financial amounts (not float)
- [ ] Foreign keys properly defined
- [ ] Consider using "database-migration" skill for best practices

### Docker & Dependencies
- [ ] `pyproject.toml` updated (if new Python package)
- [ ] TOOLS.md updated with new tool/version
- [ ] `Dockerfile` updated (if new system dependency)
- [ ] `docker-compose.yml` updated (if new environment vars/services)
- [ ] `.env.example` updated to match `.env`
- [ ] Build tested: `docker compose up --build` succeeds

### Finance Dashboard Specific Testing
- [ ] PDFs process correctly (test with real bank statements)
- [ ] No duplicate transactions on re-import (SHA-256 deduplication)
- [ ] Grafana dashboards load properly (http://localhost:3000)
- [ ] PostgreSQL queries perform well (check with EXPLAIN ANALYZE)
- [ ] Docker services healthy: `docker compose ps` shows all running
- [ ] Test with all 4 processor types: Amex, Chase, Citi, Generic

---

## 🔗 Quick Reference

### When to Use OpenSpec (Generic)

**Use OpenSpec for:**
- ✅ Any new feature (v0.2, v0.3, etc.)
- ✅ Significant bug fixes (affects architecture)
- ✅ Performance optimizations (documented approach)
- ✅ Schema/database changes
- ✅ Multi-file refactoring

**Don't use OpenSpec for:**
- ❌ Typos, quick hotfixes (commit directly)
- ❌ Adding single log line (commit directly)
- ❌ Small config adjustments (commit directly)

### When to Use Each Execution Method (Generic)

**Decision tree:**
1. Is the task repeatable across projects/conversations? → **Skill**
2. Can tasks run independently in parallel? → **Subagents** (may use Skills)
3. Otherwise → **Direct execution**

**Quick comparison:**

| Method | Use When | Don't Use When |
|--------|----------|----------------|
| **Direct** | Simple, sequential tasks | Tasks are parallelizable |
| **Skills** | Reusable procedural knowledge | One-time, project-specific logic |
| **Subagents** | Independent, parallel tasks | Tasks have dependencies |

### When to Ask Claude Code (Generic)

**Good questions:**
- "Create an OpenSpec proposal for [feature]"
- "Can you add [scenario] to the spec?"
- "The specs look good, let's implement"
- "Use [skill-name] skill to implement [task]"
- "Spawn subagents for tasks 2-4 in parallel"
- "Here's an issue during implementation, adjust approach?"
- "Please archive this change"

**Questions to avoid:**
- Vague: "Make this better" → Be specific about what/why
- Scope creep: "While you're at it, also..." → Use separate OpenSpec proposal
- Off-track: "Just add this one thing" → Breaks spec-first workflow

---

## 🔧 Common Commands

### Generic (OpenSpec)
```bash
openspec list                              # View active changes
openspec show {feature}                    # View change details
openspec validate {feature}                # Check spec formatting
openspec archive {feature} --yes           # Finalize feature
```

### Project-Specific (Finance Dashboard)

**Docker:**
```bash
docker compose up -d                       # Start services
docker compose ps                          # Check status
docker compose logs pdf-processor          # View logs
docker compose down                        # Stop services
docker compose up --build                  # Rebuild and start
```

**Database (inside container):**
```bash
docker compose exec postgres psql -U finance -d finance_db
  \d transactions                          # List columns
  \dt                                      # List all tables
  SELECT COUNT(*) FROM transactions;       # Row count
  EXPLAIN ANALYZE SELECT * FROM ...;       # Query performance
```

**Python (development):**
```bash
uv pip install -r requirements.txt         # Install dependencies
python -m pdf_processor.cli process        # Run PDF extraction
python scripts/ingestion/ingest_data.py    # Ingest CSVs
```

**Git (conventional commits):**
```bash
git checkout -b feature/v0.2-{feature}     # Create feature branch
git commit -m "feat(db): add materialized views"
git commit -m "fix(pdf): handle multiline descriptions"
git commit -m "docs: archive v0.2-{feature}"
```

---

## 📝 Notes & Tips

### Generic (OpenSpec Projects)
- **Keep specs focused:** One feature per OpenSpec change (don't mix unrelated features)
- **Spec-first workflow:** Always create proposal before implementation
- **Iterative refinement:** It's okay to refine specs multiple times before implementing
- **Archive when done:** Don't leave completed changes unarchived
- **Choose execution wisely:** Don't force subagents/skills if direct execution is simpler
- **Skills for patterns:** Create skills for logic you'll reuse across projects
- **Subagents for parallelism:** Only when tasks are truly independent

### Project-Specific (Finance Dashboard)
- **Feature branches:** Always commit to feature branch: `git checkout -b feature/v0.2-{name}`
- **Conventional commits:** Use `feat:`, `fix:`, `docs:`, `refactor:` prefixes
- **Test destructive changes:** Always test Alembic migrations (upgrade + downgrade) before committing
- **Environment variables:** Use `.env` for local development, document in `.env.example`
- **Deduplication is critical:** SHA-256 hash prevents duplicate imports
- **Docker is source of truth:** Local Python environment may differ; test in Docker
- **Financial precision:** Always use `NUMERIC`/`Decimal` for amounts, never `float`
- **PDF parsing skill:** Consider creating reusable skill for bank statement parsing patterns
- **Parallel processors:** Use subagents when implementing multiple bank processors simultaneously

---

**Last Updated:** 2026-01-07

**For current release status:** See `openspec/V0.2_OVERVIEW.md`
**For detailed feature specs:** See `openspec/changes/{feature}/proposal.md`
**For project conventions:** See `openspec/project.md`
**For tool requirements:** See `TOOLS.md`
**For execution methodology:** See Phase 2: Implementation and Execution Approaches sections above
