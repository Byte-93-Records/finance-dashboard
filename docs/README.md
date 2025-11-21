# Finance Dashboard Documentation Structure

This directory follows the **Diataxis** framework for technical documentation:
- **Tutorials** (learning-oriented): Step-by-step guides for beginners
- **How-To Guides** (task-oriented): Recipes for specific tasks
- **Reference** (information-oriented): Technical descriptions
- **Explanation** (understanding-oriented): Clarification and discussion

## Directory Structure

```
docs/
├── README.md                    # This file
├── next_features.md             # Feature roadmap (all versions)
│
├── openspec/                    # Technical specifications (BEFORE implementation)
│   ├── v0.1/                    # Completed specs for v0.1
│   │   ├── pdf_processor/
│   │   ├── csv_parser/
│   │   └── grafana_integration/
│   ├── v0.2/                    # Specs for v0.2 (to be created)
│   │   ├── bank_processors/
│   │   ├── materialized_views/
│   │   └── performance_optimization/
│   └── template.md              # Template for new OpenSpec proposals
│
├── versions/                    # Version reports (AFTER implementation)
│   ├── v0.1-initial-implementation.md
│   ├── v0.2-scale-performance.md       # To be created
│   └── v0.3-multi-source.md            # To be created
│
├── how-to/                      # 📖 How-To Guides (Diataxis)
│   ├── v0.1/
│   │   ├── 01-setup-environment.md
│   │   ├── 02-process-pdf-statements.md
│   │   ├── 03-ingest-csv-data.md
│   │   ├── 04-configure-grafana.md
│   │   └── 05-customize-dashboards.md
│   └── v0.2/                            # To be created
│
├── tutorials/                   # 🎓 Tutorials (Diataxis)
│   └── v0.1/
│       └── getting-started.md           # Complete beginner guide
│
├── reference/                   # 📚 Reference (Diataxis)
│   └── v0.1/
│       ├── database-schema.md
│       ├── csv-format.md
│       ├── environment-variables.md
│       └── filename-format.md           # Moved from root
│
└── explanation/                 # 💡 Explanation (Diataxis)
    └── v0.1/
        ├── architecture-overview.md
        ├── design-decisions.md
        └── pdf-extraction-challenges.md
```

## Diataxis Framework Explained

### 📖 How-To Guides (Task-Oriented)
**Purpose:** Help users accomplish specific tasks  
**Examples:**
- How to process a new bank's PDFs
- How to add a custom Grafana panel
- How to troubleshoot ingestion errors

**Characteristics:**
- Focused on a single task
- Assumes some knowledge
- Step-by-step instructions
- No lengthy explanations

### 🎓 Tutorials (Learning-Oriented)
**Purpose:** Guide beginners through a complete workflow  
**Examples:**
- Getting started with Finance Dashboard
- Your first transaction import
- Creating your first custom dashboard

**Characteristics:**
- Complete learning experience
- Safe to follow (no edge cases)
- Repeatable
- Inspires confidence

### 📚 Reference (Information-Oriented)
**Purpose:** Provide technical details and specifications  
**Examples:**
- Database schema documentation
- CSV format specification
- API reference
- Configuration options

**Characteristics:**
- Dry and factual
- Comprehensive
- Organized for lookup
- Accurate and up-to-date

### 💡 Explanation (Understanding-Oriented)
**Purpose:** Clarify and discuss topics  
**Examples:**
- Why we chose PostgreSQL over MongoDB
- Architecture decisions
- PDF extraction challenges and trade-offs

**Characteristics:**
- Provides context
- Discusses alternatives
- Explains "why" not "how"
- Deepens understanding

## Version-Based Organization

Each version (v0.1, v0.2, etc.) has its own subdirectories:
- **OpenSpec**: Technical specs written BEFORE implementation
- **How-To**: Practical guides written DURING/AFTER implementation
- **Reference**: Updated with each version's new features
- **Explanation**: Architecture and design decisions per version

## OpenSpec Change Management Process

### For v0.2+ Features

1. **Proposal Phase**
   - Create `docs/openspec/v0.{X}/{feature-name}/proposal.md`
   - Document problem, solution, architecture
   - Get team review

2. **Implementation Phase**
   - Create feature branch: `feature/v0.2-{feature-name}`
   - Implement according to spec
   - Update reference docs

3. **Documentation Phase**
   - Write how-to guides in `docs/how-to/v0.{X}/`
   - Update version report
   - Create explanation docs if needed

4. **Release**
   - Merge to main
   - Tag version: `git tag v0.{X}`
   - Publish release notes

## Quick Reference

| Need to... | Look in... |
|------------|-----------|
| Learn from scratch | `tutorials/v0.1/getting-started.md` |
| Complete a specific task | `how-to/v0.{X}/` |
| Check API/schema details | `reference/v0.{X}/` |
| Understand design choices | `explanation/v0.{X}/` |
| See what's planned | `next_features.md` |
| Review implementation | `versions/v0.{X}-*.md` |
| Propose new feature | `openspec/v0.{X}/{feature}/` |

## Contributing

When adding documentation:
1. Determine which Diataxis category it belongs to
2. Place in appropriate version folder
3. Use clear, descriptive filenames
4. Link related documents
5. Keep it concise and scannable

---

**Last Updated:** November 20, 2025  
**Framework:** [Diataxis](https://diataxis.fr/)
