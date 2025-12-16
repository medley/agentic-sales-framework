# Daily Prospecting Workflow

A practical guide to using the prospecting system day-to-day.

**Key Concept**: Approval means "human reviewed and approved to send outbound."
Approval does NOT create an opportunity. Approved artifacts stay in `02_Prospecting`.

## Complete Pipeline Workflow

The prospecting system runs in four stages. This is the end-to-end workflow:

### Stage 1: Run Orchestrator

Generate new prospect drafts from your Salesforce account list:

```bash
# From a CSV export
python scripts/outbound_run.py \
  --accounts data/salesforce_accounts.csv \
  --top_n 10 \
  --max_drafts_per_account 2

# Common options
#   --top_n N                     Process top N accounts by score
#   --max_drafts_per_account N    Max contacts per account (default: 3)
#   --max_total_drafts N          Max total drafts for run (default: 20)
#   --tier A|B                    Prospect tier
#   --dry_run                     Preview without processing
```

Output: Creates `runs/YYYY-MM-DD_outbound_run.json` dashboard and `draft_path` files.

### Stage 2: Review Queue

See what's ready for rendering:

```bash
python scripts/review_queue.py --only_renderable
```

### Stage 3: Render Run (Batch Renderer)

Render all prepared drafts in batch:

```bash
# Render today's run (dry run first)
python scripts/render_run.py --dry_run

# Actually render
python scripts/render_run.py

# Render specific date
python scripts/render_run.py --run_date 2025-12-11

# Options
#   --limit N           Max items to render (default: 20)
#   --only_approvable   Only render approval-eligible items
#   --force             Override review_required gate (after human review)
```

**Render Gates** - items are skipped when:
- `confidence_mode` is LOW or GENERIC
- `warnings` contain THIN_RESEARCH or VENDOR_DATA_ONLY
- `review_required` is true (override with `--force` after human review)
- `automation_allowed` is false (regulatory block - cannot be overridden)

### Stage 4: Approve for Send (Interactive)

Review and approve rendered emails:

```bash
# Interactive mode (recommended)
python scripts/approve_for_send.py \
  --company "Acme Corp" \
  --contact "John Smith" \
  --interactive

# Or see all approvable items
python scripts/review_queue.py --only_approvable
```

**Important**: Approved artifacts stay in `02_Prospecting/agent-prospecting/{Company}/approved/`.
Nothing moves to `01_Accounts/_Active` during prospecting.

---

## Morning Routine (5 minutes)

### 1. Check Your Queue

```bash
python scripts/review_queue.py
```

This shows you what needs attention today:

```
Daily Review Queue – 2025-01-15 (Wednesday)

  42 item(s) to review

  Legend: ✓ approvable  ◐ rendered  ○ prepared  ⚠ review

1) Agilent (Primary Account)
   ✓ Carly Hughes – IT – RENDERED – HIGH
     Warnings: none
     → Ready to approve

2) Varian Medical Systems
   ◐ Ali Rezaei – MFG – RENDERED – MEDIUM
     Warnings: OLD_SIGNALS_PRESENT
     → Review before approve

3) ConvaTec
   ⚠ Regulatory Persona – REVIEW – HIGH
     Warnings: none
     → Manual decision only
```

### 2. Quick Stats Check

```bash
python scripts/prospecting_stats.py --mini
```

One-line status:
```
Prepared: 42 | Rendered: 31 | Approved: 18 | Stalled: 12%
```

## During the Day

### Inbox View

When you want a quick overview:

```bash
python scripts/inbox_view.py --actionable_only --limit 20
```

Compact view:
```
[+] 2025-01-15  Agilent          Carly Hughes      IT   HI   APPROVE!
[R] 2025-01-15  Varian           Ali Rezaei        MFG  MD   RENDERED
[!] 2025-01-15  ConvaTec         Reg Person        REG  HI   REVIEW
[.] 2025-01-15  BioMerieux       John Smith        QUA  MD   PREPARED
```

Legend:
- `[+]` approvable - ready to approve for send
- `[R]` rendered - needs review
- `[.]` prepared - needs rendering
- `[!]` review required - manual decision
- `[A]` approved - done

### Filter Your View

By confidence:
```bash
python scripts/review_queue.py --confidence HIGH --only_approvable
```

By persona:
```bash
python scripts/review_queue.py --persona quality
```

Ready to render:
```bash
python scripts/review_queue.py --only_renderable
```

## Approving Artifacts

### Quick Approve (Know What You're Doing)

```bash
python scripts/approve_for_send.py \
  --company "Agilent" \
  --contact "Carly Hughes"
```

### Interactive Approve (Recommended)

```bash
python scripts/approve_for_send.py \
  --company "Agilent" \
  --contact "Carly Hughes" \
  --interactive
```

This shows you:
1. Full email preview
2. Context quality header
3. Any warnings
4. Asks for confirmation
5. Optional: add a note

### Dry Run First

Not sure? Preview without committing:

```bash
python scripts/approve_for_send.py \
  --company "Agilent" \
  --contact "Carly Hughes" \
  --dry_run
```

## When to Render

Render when:
- Status is `prepared_for_rendering`
- No blocking warnings
- `review_required` is false

Don't render when:
- `THIN_RESEARCH` warning present
- `review_required` is true
- Regulatory persona (unless you're sure)

```bash
# See what's ready to render
python scripts/review_queue.py --only_renderable
```

## When to Approve

Approve when:
- Status is `rendered_validated`
- Confidence is HIGH or MEDIUM
- No blocking warnings
- Email looks good on review

Don't approve when:
- `THIN_RESEARCH` warning (can't force)
- `VENDOR_DATA_ONLY` warning (can't force)
- Confidence is GENERIC
- Something feels off (trust your gut)

## Handling Warnings

### Warning Reference

| Warning | Meaning | Can Force? | Action |
|---------|---------|------------|--------|
| `OLD_SIGNALS_PRESENT` | Data is stale (>1 year old) | Yes | Review, maybe re-research |
| `THIN_RESEARCH` | Few signals, stale data | No | Re-research or skip |
| `VENDOR_DATA_ONLY` | No citable sources | No | Re-research |
| `NO_CITED_SIGNALS` | Nothing to cite | - | Use generic approach |
| `COMPANY_INTEL_STALE` | Company data expired | Yes | Re-fetch company intel |
| `REVIEW_REQUIRED` | Persona needs review | Yes | Check before proceeding |

### Force Override

Only use `--force` when:
- You've reviewed the content manually
- You understand why the warning exists
- The warning is forceable (not THIN_RESEARCH or VENDOR_DATA_ONLY)

```bash
python scripts/approve_for_send.py \
  --company "Acme" \
  --contact "John" \
  --force
```

## Review Required Items

These need manual attention:

1. **Regulatory personas** - Always review before any action
2. **Ambiguous personas** - System wasn't sure, you decide
3. **Low confidence** - Thin data, verify before sending

For these:
```bash
# See all review items
python scripts/review_queue.py --persona regulatory
```

Then either:
- Skip them entirely
- Research more before proceeding
- Force if you're confident

## Weekly Review

### Full Stats

```bash
python scripts/prospecting_stats.py --days 7
```

Look at:
- **Stalled %** - If high, pipeline is stuck
- **Top warnings** - What's blocking progress
- **Best persona** - Where you're winning

### Group by Company

```bash
python scripts/inbox_view.py --group_by company
```

See which accounts have multiple contacts ready.

### Group by Persona

```bash
python scripts/inbox_view.py --group_by persona
```

See how different personas are performing.

## Troubleshooting

### "No artifacts found"

The prospecting root might not be set. Check:
```bash
echo $PROSPECTING_OUTPUT_ROOT
```

Default: `~/prospecting-output` (configurable via PROSPECTING_OUTPUT_ROOT)

### "Cannot force approval"

These warnings cannot be overridden:
- `THIN_RESEARCH`
- `VENDOR_DATA_ONLY`

You need to re-research or skip.

### "Review required"

The persona or content needs human review. Options:
1. Use `--force` (if you've reviewed)
2. Skip this contact
3. Re-research with different angle

### Stalled items piling up

Check why:
```bash
python scripts/review_queue.py --only_renderable
```

If empty, items are blocked by:
- Review required
- Warnings
- Already rendered but not approved

## Quick Reference

| Task | Command |
|------|---------|
| Run orchestrator | `python scripts/outbound_run.py --accounts FILE.csv --top_n N` |
| Morning queue | `python scripts/review_queue.py` |
| Quick stats | `python scripts/prospecting_stats.py --mini` |
| Inbox view | `python scripts/inbox_view.py --actionable_only` |
| Batch render | `python scripts/render_run.py` |
| Render dry run | `python scripts/render_run.py --dry_run` |
| Approve (interactive) | `python scripts/approve_for_send.py --company X --contact Y --interactive` |
| Dry run | Add `--dry_run` to any approve command |
| Filter HIGH only | Add `--confidence HIGH` |
| Filter persona | Add `--persona quality` |
| Force override | Add `--force` (use carefully) |

## Best Practices

1. **Start with the queue** - Know what needs attention
2. **Use interactive mode** - Review before committing
3. **Don't force blindly** - Understand why something's blocked
4. **Trust the warnings** - They exist for a reason
5. **Check weekly stats** - Spot patterns early
6. **Regulatory = careful** - Always review these manually
7. **Approval ≠ Opportunity** - Approved drafts stay in prospecting
