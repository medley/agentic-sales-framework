# Prospecting Architecture Patterns

> Design patterns and architectural decisions for the hybrid prospecting pipeline.

This document explains the key architectural patterns that make the system work reliably at scale. These patterns are applicable to any B2B sales automation system, not just the specific implementation here.

---

## Four-Phase Pipeline

The system processes prospects through four distinct phases, each with clear inputs, outputs, and failure modes.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PROSPECTING PIPELINE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Phase 1: RESEARCH          Phase 2: EXTRACTION       Phase 3: SCORING     │
│  ──────────────────        ─────────────────────     ────────────────────  │
│  ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐   │
│  │ Web Search      │       │ Signal          │       │ LLM Angle       │   │
│  │ (Perplexity)    │──────▶│ Extraction      │──────▶│ Scorer          │   │
│  └─────────────────┘       └─────────────────┘       └─────────────────┘   │
│  ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐   │
│  │ Data Enrichment │       │ Tier            │       │ Deterministic   │   │
│  │ (ZoomInfo)      │──────▶│ Assignment      │──────▶│ Fallback        │   │
│  └─────────────────┘       └─────────────────┘       └─────────────────┘   │
│  ┌─────────────────┐       ┌─────────────────┐                             │
│  │ SEC/Public Data │       │ Persona         │                             │
│  │ (EDGAR, etc.)   │──────▶│ Detection       │                             │
│  └─────────────────┘       └─────────────────┘                             │
│                                                                             │
│                                    │                                        │
│                                    ▼                                        │
│                                                                             │
│  Phase 4: GENERATION                                                        │
│  ──────────────────────────────────────────────────────────────────────────│
│  ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐   │
│  │ Template        │       │ LLM             │       │ 6-Layer         │   │
│  │ Selection       │──────▶│ Renderer        │──────▶│ Validation      │   │
│  └─────────────────┘       └─────────────────┘       └─────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Phase 1: Research Orchestration

**Purpose**: Gather raw data from multiple sources.

**Key patterns**:
- **Parallel fetching**: Query multiple sources simultaneously
- **Graceful degradation**: If one source fails, continue with others
- **90-day caching**: Avoid redundant API calls for repeat prospects

**Sources by type**:
| Source | Data Type | Cacheable |
|--------|-----------|-----------|
| Perplexity | Company news, events | 30 days |
| ZoomInfo | Contact info, org data | 90 days |
| SEC EDGAR | Financials, filings | 90 days |
| Web scraping | Company websites | 7 days |

---

### Phase 2: Signal Extraction & Tiering

**Purpose**: Transform raw data into actionable, citable signals.

#### The Signal Model

Every signal has three critical properties:

```python
Signal = {
    "text": str,           # Human-readable description
    "source_type": str,    # Where it came from
    "source_url": str,     # Citation link (if available)
    "citability": str,     # Can we reference this explicitly?
}
```

**Source types and their usage rules**:

| Source Type | Can Make Explicit Claims? | Example |
|-------------|---------------------------|---------|
| `public_url` | ✅ Yes - cite the URL | "Per your recent press release..." |
| `user_provided` | ✅ Yes - user validated | "As you mentioned to [colleague]..." |
| `vendor_data` | ❌ No - guides strategy only | Use industry language instead |
| `inferred` | ❌ No - generic only | "Many companies in [industry]..." |

**Why this matters**: Vendor data (ZoomInfo, etc.) is not publicly verifiable. If we say "I saw you're expanding to 200 employees" based on ZoomInfo data, the recipient might wonder how we know that. Public URLs are safe to reference.

#### Tier Assignment

Prospects are tiered based on signal quality:

| Tier | Cited Signals Required | Email Personalization Level |
|------|------------------------|----------------------------|
| A | 3+ | Full personalization with specific claims |
| B | 2 | Company mentions, limited specificity |
| C | 1 | Industry language, general pain points |
| D | 0 | Generic template only |

**The tier determines the confidence mode** (see Phase 4).

#### Persona Detection

Title patterns map to personas for angle selection:

```yaml
personas:
  quality:
    patterns: ["vp quality", "director qa", "quality assurance"]
  operations:
    patterns: ["coo", "vp operations", "director operations"]
  it:
    patterns: ["cio", "vp it", "director it", "head of technology"]
```

**Fallback**: Unknown titles default to a generic persona with broader angle eligibility.

---

### Phase 3: Angle Scoring

**Purpose**: Select the optimal messaging angle for this prospect.

#### Hybrid Approach

The system uses **deterministic filtering** followed by **LLM scoring**:

```
Step 1: FILTER (Deterministic)
──────────────────────────────
All angles → Filter by:
  - Persona eligibility
  - Product eligibility
  - Industry match
  - Required signal presence
→ Candidate angles (3-5)

Step 2: SCORE (LLM)
───────────────────
Candidate angles → LLM scores:
  - Relevance (1-5)
  - Urgency (1-5)
  - Reply likelihood (1-5)
→ Weighted ranking

Step 3: SELECT (Deterministic)
──────────────────────────────
Ranked angles → Deterministic tiebreaker:
  - Highest weighted score wins
  - Same score? Use priority order
→ Final angle
```

#### Why Not Pure LLM Selection?

1. **Reproducibility**: Same inputs → same output (for debugging)
2. **Auditability**: Can explain exactly why an angle was chosen
3. **Safety**: LLM can't invent angles that bypass product rules
4. **Cost**: LLM only scores 3-5 candidates, not 20+ angles

#### Scoring Weights

```python
scoring_weights = {
    "relevance": 0.45,      # How well does angle match signals?
    "urgency": 0.35,        # Is there time pressure?
    "reply_likelihood": 0.20 # Will they actually respond?
}
```

---

### Phase 4: Generation & Validation

**Purpose**: Render the email and validate it against constraints.

#### Confidence Modes

The tier determines what the LLM is allowed to generate:

| Mode | Tier | Allowed Content |
|------|------|-----------------|
| HIGH | A | Explicit company claims: "Your recent acquisition of X..." |
| MEDIUM | B | Company references: "Companies like yours often..." |
| LOW | C | Industry language: "In the pharmaceutical industry..." |
| GENERIC | D | Template only: "I work with companies in your space..." |

**This is enforced at generation time AND validated post-generation**.

#### 6-Layer Validation Pipeline

Every generated email passes through:

```
Layer 1: STRUCTURE
──────────────────
- Word count (50-100)
- Has greeting
- Has signature
- Single paragraph (mobile-friendly)

Layer 2: SIGNAL INTEGRITY
─────────────────────────
- Every claim traces to a signal
- Cited signals have source_url
- No claims from vendor_data sources

Layer 3: CONFIDENCE COMPLIANCE
──────────────────────────────
- HIGH mode: Must have explicit claims
- LOW mode: Must NOT have explicit claims
- Mode matches tier assignment

Layer 4: VOICE CONSISTENCY
──────────────────────────
- Matches defined persona
- No banned phrases ("hope this finds you")
- Ends with question (Sandler pattern)

Layer 5: PRODUCT SAFETY
───────────────────────
- Only mentions eligible products
- No forbidden product references
- Persona/product matrix enforced

Layer 6: QUALITY CONTROLS
─────────────────────────
- No hallucinated company names
- No fabricated statistics
- No speculative claims
```

#### Repair Loop

If validation fails, the system attempts repair:

```
Generate → Validate → FAIL
              ↓
         Repair (temp=0.3) → Validate → FAIL
              ↓
         Repair (temp=0.3) → Validate → FAIL
              ↓
         Fallback to GENERIC mode
```

**Max 2 repair attempts** to avoid infinite loops.

---

## Key Design Decisions

### 1. Deterministic First, LLM Second

The system uses deterministic logic wherever possible:
- **Persona detection**: Pattern matching, not LLM classification
- **Tier assignment**: Signal count, not LLM judgment
- **Angle filtering**: Rule-based eligibility
- **Final selection**: Weighted scores with deterministic tiebreaker

LLM is used only where creativity adds value:
- **Angle scoring**: Nuanced relevance assessment
- **Email rendering**: Natural language generation
- **Repair attempts**: Creative problem-solving

### 2. Fail Safe, Not Fail Silent

When something goes wrong:
- **Missing data**: Degrade to lower tier, don't fake it
- **Validation failure**: Fall back to generic, don't skip validation
- **API error**: Use cached data, don't proceed without data

### 3. Auditability Over Automation

Every decision is traceable:
- **Signal provenance**: source_type + source_url for every claim
- **Angle selection**: Full scoring breakdown in output
- **Validation results**: Layer-by-layer pass/fail with reasons

### 4. Mobile-First Email Design

All emails are optimized for mobile:
- **50-100 words**: Readable on phone
- **Single paragraph**: No scrolling required
- **Question ending**: Clear call-to-action visible

---

## Extension Points

The architecture supports customization without core changes:

| What | Where | How |
|------|-------|-----|
| Add persona | `rules/base_config.yaml` | Add patterns + eligibility |
| Add angle | `rules/base_config.yaml` | Add angle + constraints |
| Add product | `rules/base_config.yaml` | Add product + persona mapping |
| Add validation | `validators.py` | Add new validation function |
| Add data source | `company_intel/providers/` | Implement BaseProvider |

---

## Performance Characteristics

| Operation | Typical Time | Bottleneck |
|-----------|--------------|------------|
| Research (cached) | <1s | Disk I/O |
| Research (fresh) | 5-15s | API calls |
| Signal extraction | <100ms | CPU |
| Angle scoring | 2-4s | LLM API |
| Email generation | 3-5s | LLM API |
| Validation | <100ms | CPU |

**Total (cached)**: ~6-10s per prospect
**Total (fresh)**: ~15-25s per prospect

---

## Testing Strategy

| Layer | Test Type | Coverage |
|-------|-----------|----------|
| Signal extraction | Unit | Deterministic, 100% |
| Persona detection | Unit | Pattern matching, 100% |
| Tier assignment | Unit | Boundary conditions |
| Angle filtering | Unit | Eligibility rules |
| Validation | Unit | Each layer independently |
| Full pipeline | Integration | End-to-end scenarios |

**Key principle**: Test deterministic components exhaustively, mock LLM for integration tests.
