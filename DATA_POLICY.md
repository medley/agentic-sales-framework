# Data Policy

This repository contains **no customer data, proprietary information, or personally identifiable information (PII)**.

## What This Repo Contains

- **Synthetic examples only** - All company names, contact names, and deal scenarios are fictional (e.g., "Northwind Manufacturing", "Acme Pharma", "John Smith")
- **Public methodology references** - Sales methodologies like Sandler and MEDDPICC are publicly documented frameworks
- **Architecture and code patterns** - The system design and implementation patterns, not customer-specific content

## What This Repo Does NOT Contain

- Customer names, logos, or confidential deal information
- Scraped or harvested personal data
- Private call transcripts, emails, or meeting notes
- API keys, credentials, or secrets (only `.env.example` placeholders)
- Internal company documents or proprietary playbooks

## Data Separation by Design

The architecture enforces separation between code and data:

```
sample-data/          # Fictional examples only (committed)
├── input/            # Empty scaffolding
└── Runtime/          # Empty scaffolding with .gitkeep files

Real data (not in repo):
~/OneDrive/Accounts/  # Actual deal folders (gitignored, never committed)
```

## For Users of This Framework

When you use this framework with real data:

1. **Keep real data outside the repo** - Use environment variables or symlinks
2. **Never commit customer data** - The `.gitignore` excludes common data paths
3. **Review before pushing** - Use `git status` to verify no sensitive files are staged

## Verification

To verify this repo contains no secrets or sensitive data:

```bash
# Scan for secrets in git history
gitleaks detect --source . --verbose

# Check for common PII patterns
grep -r "@company\.com" --include="*.py" --include="*.md" .
```

This repository has been scanned with gitleaks before publication.
