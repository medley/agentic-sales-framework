# Data Precedence Rules

When multiple sources provide conflicting information about the same field, apply this hierarchy.

---

## Precedence Hierarchy

**CRM Export > Quote Document > Call Transcript > Email/Notes > Generic Files**

### Rationale
- **CRM data is authoritative** - Represents official system of record
- **Quote data is contractual** - Represents formal commercial agreements
- **Transcript data is conversational** - May be approximate or exploratory
- **Email/notes are informal** - Often outdated or preliminary

---

## Field-by-Field Precedence Rules

### ACV (Annual Contract Value)

**Precedence:**
1. CRM "ACV" or "Annual Contract Value" field
2. Quote "Total Annual" or "Annual Contract Value" line item
3. Transcript mention of annual budget or contract value
4. Email mention of budget
5. If unclear or conflicting → "TBD"

**Example:**
- CRM says: $144,000
- Quote says: $150,000 annual
- Transcript says: "around $140K"
- **Result:** Use CRM value ($144,000)

**Example:**
- Quote says: $150,000 annual
- Transcript says: "budget is approximately $140K"
- No CRM data
- **Result:** Use Quote value ($150,000)

---

### Close Date

**Precedence:**
1. CRM "Close Date" or "Expected Close" field
2. Quote expiration date (if reasonably aligned with deal timeline)
3. Transcript mention of target decision date or deadline
4. Email mention of timeline
5. If unclear → "TBD"

**Example:**
- CRM says: 2025-12-31
- Quote expires: 2026-01-15
- Transcript says: "we'd like to decide by end of year"
- **Result:** Use CRM value (2025-12-31)

**Note:** Quote expiration is often later than actual close date. Only use if no other source exists.

---

### Economic Buyer

**Precedence:**
1. CRM "Economic Buyer" field (explicit)
2. Transcript identification of budget authority/decision maker
3. Email from or mentioning person with budget authority
4. If unclear → "UNKNOWN"

**Example:**
- CRM Economic Buyer: Jane Smith (VP Finance)
- Transcript: John Doe mentions "I'll need to check with the VP"
- **Result:** Use CRM (Jane Smith, VP Finance)

---

### Champion

**Precedence:**
1. Transcript evidence of internal advocacy/support
2. Email evidence of proactive help from contact
3. CRM "Champion" field (if present)
4. If unclear → "UNKNOWN"

**Note:** Champion is relationship-based, often better identified in transcripts than CRM fields.

**Example:**
- CRM Champion: John Doe
- Transcript: John says "I'll help you navigate our procurement process"
- **Result:** Confirm John Doe as champion

---

### Competition

**Precedence:**
1. CRM "Competitors" or "Competition" field
2. Transcript mentions of alternatives being evaluated
3. Email mentions of other vendors
4. If none → "UNKNOWN"

**Example:**
- CRM Competitors: Acme Corp, Beta Systems
- Transcript: "We're also talking to Acme and another vendor"
- **Result:** Use CRM list (Acme Corp, Beta Systems)

**Example:**
- Transcript: "Looking at Toys R Us and Target as alternatives"
- No CRM data
- **Result:** Use transcript (Toys R Us, Target)

---

### Stage

**Precedence:**
1. CRM "Stage" or "Opportunity Stage" field
2. Activity-based inference (e.g., quote sent → later stage)
3. If unclear → "1-Discovery"

**Do NOT override CRM stage based on activities.** CRM is authoritative for stage.

**Example:**
- CRM Stage: 2-Discovery
- Quote sent (would suggest 3-Validation)
- **Result:** Use CRM (2-Discovery) and note discrepancy in Risks section

---

### Pain Points

**Precedence:**
1. Customer quotes from transcript (highest fidelity)
2. CRM fields describing pain/challenges
3. Email mentions of problems
4. If none → empty array

**Note:** Pain points from transcripts are usually more detailed/specific than CRM summaries.

**Approach:**
- Use transcript pain quotes as primary
- Supplement with CRM pain if additional context
- Do NOT duplicate (if transcript covers what's in CRM, prefer transcript)

---

### Metrics / KPIs

**Precedence:**
1. Transcript exact quotes with numbers (e.g., "batch reviews take 3-4 days")
2. CRM metric fields
3. Email mentions of metrics
4. If none → empty array

**Example:**
- Transcript: "Our manual process takes 3-4 days per batch"
- CRM: Custom field "Cycle Time: 5 days"
- **Result:** Use transcript (3-4 days) - more specific and sourced

---

### Timeline / Target Dates

**Precedence:**
1. Explicit dates from any source (exact date > approximate timeframe)
2. CRM dates if multiple dates conflict
3. Transcript mentions if no CRM data

**Example:**
- Transcript: "We need to decide by December 10th, 2025"
- Email: "Hoping to wrap this up before year-end"
- **Result:** Use transcript (2025-12-10) - more specific

---

## Conflict Resolution Examples

### Example 1: CRM vs. Quote Pricing Conflict

**Sources:**
- CRM ACV: $120,000
- Quote Total Annual: $144,000

**Resolution:**
Use CRM value ($120,000) but note in deal.md:
- Frontmatter acv: $120,000
- Risks section: "Pricing discrepancy: CRM shows $120K but latest quote is $144K - verify with AE"

**Rationale:** CRM is authoritative, but discrepancy may indicate:
- Quote is newer (needs CRM update)
- Quote includes add-ons not in CRM
- Error in one system

---

### Example 2: Transcript vs. Email Timeline

**Sources:**
- Transcript (Jan 15): "We'd like to close by March 31"
- Email (Jan 20): "Actually, we need to push to April 30 due to budget cycle"

**Resolution:**
Use Email (2025-04-30) - more recent information.

**Principle:** When sources have different dates, **use the most recent source** unless CRM explicitly overrides.

---

### Example 3: Multiple Stakeholders Across Sources

**Sources:**
- CRM Contacts: Jane Smith (VP Finance), John Doe (Director IT)
- Transcript: Mentions Jane Smith, John Doe, and Sarah Johnson (Procurement)
- Email: From Jane Smith

**Resolution:**
Merge all stakeholders:
- Jane Smith (VP Finance) - from CRM + transcript + email
- John Doe (Director IT) - from CRM + transcript
- Sarah Johnson (Procurement) - from transcript

**Principle:** Stakeholders are additive (combine all sources), not conflicting. If titles differ, prefer CRM title.

---

### Example 4: Champion Identification Across Sources

**Sources:**
- CRM Champion: John Doe
- Transcript: Jane Smith says "I'll advocate for this internally and help you navigate procurement"
- Email: John Doe sends brief responses, Jane Smith sends detailed follow-ups

**Resolution:**
Champion: Jane Smith (based on transcript evidence of advocacy + proactive email behavior)
Update CRM champion field in suggested updates.

**Principle:** Champion is relationship-based. Transcript/email behavior evidence > CRM field.

---

## Special Cases

### Case: CRM Data is Stale

**Scenario:** CRM Close Date is 2024-12-31 (past), but current transcript (Jan 2025) discusses active deal.

**Resolution:**
- Note in Risks: "CRM close date is in the past (2024-12-31) - deal likely slipped, needs CRM update"
- Suggested close date: Based on current transcript timeline
- Flag for AE to update CRM

**Don't blindly use stale CRM data if clearly outdated.**

---

### Case: Quote Pricing Higher Than Transcript Discussion

**Scenario:**
- Transcript: "Our budget is around $100K"
- Quote: $150K total

**Resolution:**
- Use Quote ($150K) for ACV
- Note in Pain/Budget section: "Budget discussed at $100K, quote sent at $150K - potential gap"
- Suggested update confidence: "medium" (gap may indicate negotiation needed)

---

### Case: No CRM Data Available

**Scenario:** Deal intake on brand new opportunity, no CRM record yet.

**Resolution:**
- Use best available source (Quote > Transcript > Email)
- Mark confidence as "medium" or "low" in suggested updates
- Note in summaryBullets: "No CRM data available - values from [source]"

---

## Summary: Applying Precedence Rules

### Step-by-Step Process

1. **Identify all sources** mentioning the field (CRM, Quote, Transcript, Email)
2. **Apply hierarchy** (CRM > Quote > Transcript > Email)
3. **Use highest-precedence source** for suggestedUpdates.value
4. **Note discrepancies** in Risks section if conflict is significant
5. **Include ALL sources** in sourceFiles/sourceSnippets for provenance

### Example Application

**Field:** ACV
**Sources:**
- CRM: $144,000
- Quote: $150,000
- Transcript: "approximately $140K"

**Envelope output:**
```json
{
  "suggestedUpdates": {
    "acv": {
      "value": 144000,
      "confidence": "high",
      "rationale": "CRM authoritative value ($144K), Quote shows $150K, Transcript mentioned ~$140K",
      "sourceFiles": [
        "raw/other/crm_export.csv",
        "raw/quotes/quote_2025-01-15.pdf",
        "raw/calls/discovery_transcript.md"
      ],
      "sourceSnippets": [
        "CRM ACV field: $144,000",
        "Quote Total Annual: $150,000",
        "Transcript: 'budget is approximately $140K'"
      ]
    }
  }
}
```

**Note:** Include all sources in sourceSnippets for transparency, but value uses highest-precedence source.

---

## When to Flag Discrepancies

**Flag in Risks section if:**
- Discrepancy > 20% (e.g., $100K vs. $150K)
- Timeline differs by > 1 month
- Stakeholder roles conflict (e.g., CRM says "Champion", transcript shows blocker behavior)

**Don't flag if:**
- Minor rounding differences ($144K vs. $145K)
- Date format differences (same date, different format)
- Additional context in one source (not conflicting, just more detail)

---

## Quick Reference Table

| Field | Source 1 (Highest) | Source 2 | Source 3 | Source 4 | Default |
|-------|-------------------|----------|----------|----------|---------|
| ACV | CRM | Quote | Transcript | Email | TBD |
| Close Date | CRM | Quote Exp | Transcript | Email | TBD |
| Economic Buyer | CRM | Transcript | Email | - | UNKNOWN |
| Champion | Transcript | Email | CRM | - | UNKNOWN |
| Competition | CRM | Transcript | Email | - | UNKNOWN |
| Stage | CRM | Activity | - | - | 1-Discovery |
| Pain Points | Transcript | CRM | Email | - | [ ] |
| Metrics | Transcript | CRM | Email | - | [ ] |
