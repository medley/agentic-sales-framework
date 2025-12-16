# Framework

Portable knowledge layer containing methodologies, templates, and system documentation. This layer is versioned and travels with you between companies.

## Directory Structure

```
Framework/
├── Methodologies/     # Sales methodology adapters (Sandler, MEDDPICC, etc.)
├── Plays/             # Reusable sales plays (champion building, POC, etc.)
├── Style/             # Industry-specific style guides and patterns
├── System/            # Architecture docs and developer guides
└── Templates/         # Document templates for deal artifacts
```

## Key Principle

**Read-only at runtime.** Skills read from this layer but never write to it. All generated artifacts go to `sample-data/Runtime/`.

## Subdirectories

### Methodologies/
Sales methodology definitions and stage inventories. The framework supports methodology-aware coaching - if a deal specifies `methodology: Sandler`, the coaching skill loads the appropriate stage criteria.

### Plays/
Situational sales plays for specific scenarios:
- Champion building
- Executive engagement
- POC/pilot management
- Contract negotiation
- Multi-threading

### Style/
Industry-specific writing patterns and validation rules. Used by email generation to match voice and tone expectations.

### System/
Core documentation:
- `ARCHITECTURE.md` - System design and three-layer separation
- `DEVELOPER_GUIDE.md` - How to extend the framework
- `SETUP.md` - Installation and configuration
- `methodology_loader.md` - Protocol for loading methodology context

### Templates/
Starting points for deal artifacts. Skills use these as scaffolding when generating new documents.

## Extending the Framework

To add a new methodology:
1. Create `Methodologies/{Name}.md` with stage definitions
2. Add stage inventory to `sample-data/Runtime/_Shared/knowledge/methodologies/`
3. Reference in deal frontmatter: `methodology: {Name}`

See `System/DEVELOPER_GUIDE.md` for complete extension protocols.
