# Runtime Directory

Generated and processed content. Skills write here.

## Structure

- **Dashboard/** - Aggregated views and pipeline reports
- **Sessions/{DEAL_ID}/** - Per-deal workspaces (created automatically)
- **_Shared/** - Cross-deal resources and converted knowledge

## Sessions

Each deal gets its own directory under `Sessions/`. The directory name should match your deal identifier (company name, opportunity ID, etc.).

Example:
```
Sessions/
├── acme-corp/
│   ├── deal-intake/
│   │   └── deal_note.md
│   └── raw/
│       └── discovery_call.md
└── globex-industries/
    ├── deal-intake/
    └── raw/
```

## _Shared

Contains converted content that applies across all deals:
- `knowledge/methodologies/` - Processed methodology content
- `knowledge/brand/` - Brand voice and messaging
- `profile/` - Your professional profile and preferences
- `style/` - Writing samples for voice matching
