# sample-data

This directory contains your company-specific data. It is gitignored by default.

## Structure

```
sample-data/
├── input/                    # Source files (immutable - never modified by skills)
│   ├── battlecards/          # Competitive intelligence documents
│   ├── call_transcripts/     # Meeting recordings/transcripts
│   ├── email_threads/        # Email conversations for context
│   ├── personas/             # Buyer persona documents
│   ├── playbooks/            # Sales playbooks
│   │   └── methodologies/    # Methodology source materials (Sandler, etc.)
│   └── product_docs/         # Product documentation, datasheets
│
└── Runtime/                  # Generated and processed content
    ├── Dashboard/            # Aggregated views and reports
    ├── Sessions/             # Per-deal workspaces
    │   └── {DEAL_ID}/        # Each deal gets its own directory
    │       ├── deal-intake/  # Processed deal information
    │       └── raw/          # Unprocessed artifacts
    └── _Shared/              # Cross-deal resources
        ├── brand/            # Company brand guidelines
        │   └── assets/       # Logos, images
        ├── knowledge/        # Converted/structured content
        │   ├── brand/        # Brand voice, messaging
        │   └── methodologies/ # Processed methodology content
        ├── profile/          # User profile and preferences
        └── style/            # Writing style samples
```

## Usage

1. **input/** - Drop your source files here. Skills read from this directory but never modify it.
2. **Runtime/** - Skills write generated content here. Deal-specific artifacts go in `Sessions/{DEAL}/`.
3. **_Shared/** - Convert source documents to structured knowledge using the document conversion skills.

## Security Note

This entire directory should remain gitignored. It contains company IP that stays with your employer.
