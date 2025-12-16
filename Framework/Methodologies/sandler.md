# Sandler Methodology Adapter

## Overview

The Sandler Selling System (also known as the "Submarine" model) is a qualification-focused sales methodology developed by David Sandler. Unlike traditional sales approaches that rush to present solutions, Sandler emphasizes thorough qualification through Pain, Budget, and Decision criteria BEFORE delivering any presentation.

**Core Philosophy:** "You can't lose what you don't have" - disqualify early and often to avoid wasting time on prospects who won't buy.

## Key Principles

1. **No Free Consulting:** Never present solutions without completing full qualification
2. **Equal Business Stature:** Seller and buyer are equals, not vendor/customer hierarchy
3. **Qualify Before Presenting:** Pain → Budget → Decision must all be confirmed before Fulfillment
4. **Emotional vs. Intellectual:** Seek emotional commitment, not just intellectual agreement
5. **Disqualification is Success:** Disqualifying a bad-fit prospect is as valuable as closing a good-fit deal
6. **Control Through Process:** Following the system gives control without being controlling
7. **No Mutual Mystification:** Both parties always clear on where they stand

## The Submarine Model (7 Compartments)

```
┌──────────┬──────────┬──────┬────────┬──────────┬────────────┬───────────┐
│ Bonding  │ Up-Front │ Pain │ Budget │ Decision │ Fulfillment│ Post-Sell │
│ &Rapport │ Contract │      │        │          │            │           │
└──────────┴──────────┴──────┴────────┴──────────┴────────────┴───────────┘
  Foundation            Qualifying Stages        Closing Stages
  (Continuous)          (Disqualify here)        (After qualification)
```

### Foundation Stages (Continuous Throughout)
- **Bonding & Rapport:** Build trusted advisor relationship vs. vendor status
- **Up-Front Contracts:** Establish clear expectations for every interaction

### Qualifying Stages (Gate with Disqualification Criteria)
- **Pain:** Uncover compelling emotional reasons to change
- **Budget:** Confirm willingness AND ability to invest
- **Decision:** Understand decision process and access decision makers

### Closing Stages (Only After Full Qualification)
- **Fulfillment:** Present solutions matched to qualified pains; obtain decision
- **Post-Sell:** Cement close, prevent buyer's remorse, set stage for referrals

## How This Adapter Maps to Default Inventory

| Sandler Stage | Maps to Default Stage | Key Differences |
|---------------|----------------------|-----------------|
| Bonding & Rapport | All stages | Sandler treats as continuous foundation |
| Up-Front Contracts | All stages | Sandler establishes contract for each interaction |
| Pain | Stage 1: Discover | Sandler requires emotional commitment, not just needs identification |
| Budget | Stage 3: Propose | Sandler discusses budget BEFORE proposal, not after |
| Decision | Stage 4: Select | Sandler maps decision process before competing |
| Fulfillment | Stages 3-4: Propose/Select | Sandler presents AFTER qualification complete |
| Post-Sell | Stage 7: Won + beyond | Sandler emphasizes preventing buyer's remorse |

**Critical Difference:** Sandler qualifies Pain/Budget/Decision BEFORE any presentation. Default inventory spreads qualification across multiple stages and may present before full qualification.

## When to Use Sandler Methodology

**Best For:**
- Complex B2B sales with multiple decision makers
- High-value deals where qualification ROI is high
- Sales cycles where "tire-kickers" waste significant time
- Industries where buyer's remorse or deal fallout is common
- Selling situations requiring emotional commitment (change management, disruption)

**Consider Alternatives When:**
- Transactional, low-value sales (overhead too high)
- Single-decision-maker scenarios (less qualification needed)
- Product-led growth models (buyer self-qualifies)
- Highly competitive bids where access to qualification is limited

## Using This Adapter

### For Deals

**Reference the stage inventory:**
```
sample-data/Runtime/_Shared/knowledge/methodologies/Sandler/stage_inventory__Sandler.md
```

**In your deal note, specify:**
```yaml
methodology_adapter: "../../../Framework/Methodologies/sandler.md"
stage_ref: "../../_Shared/knowledge/methodologies/Sandler/stage_inventory__Sandler.md"
```

### For Coach Agent

Coach agent will:
1. Check deal against Sandler stage exit criteria
2. Identify missing required artifacts
3. Flag risk indicators (deal stalling)
4. Highlight momentum signals (deal progressing)
5. Recommend disqualification if criteria unmet

### For Skills

The following skills align with Sandler stages:

- **Bonding & Rapport:** prep_discovery, stakeholder_mapping
- **Up-Front Contracts:** agenda_internal, agenda_customer
- **Pain:** prep_discovery, pain_discovery
- **Budget:** budget_discussion, roi_outline
- **Decision:** demo_prep, executive_brief, stakeholder_mapping
- **Fulfillment:** demo_prep, presentation_builder
- **Post-Sell:** handover_builder, referral_request

## Key Sandler Techniques

### The Pain Funnel (8 Sequential Questions)
1. "Tell me more about that..."
2. "Can you be more specific? Give me an example."
3. "How long has that been a problem?"
4. "What have you tried to do about that?"
5. "And did that work?"
6. "How much do you think that has cost you?"
7. "How do you feel about that?"
8. "Have you given up trying to deal with the problem?"

### Budget Discussion Approaches
- **Third-Party Story:** Share similar project costs, ask if comfortable in that range
- **Bracketing:** Provide range based on variables, ask where they fall
- **Direct Ask:** "In round numbers, what amount do you have in mind?"

### Decision Process Mapping
- **Newspaper Reporter:** Who, What, When, Where, How, Why
- **Cast of Characters:** Map all participants with roles, pains, and sentiment
- **Timeline Identifier:** Work backward from implementation date

### Negative Reverse Selling
Reduce pressure by suggesting the prospect might NOT want your solution:
- "It may not be a fit"
- "I'm not sure we can help you"
- "You should probably tell me 'no' if you're not 100% comfortable"

## Common Pitfalls to Avoid

1. **Presenting Too Early:** Rushing to Fulfillment before Pain/Budget/Decision complete
2. **Intellectual vs. Emotional:** Accepting "thinking about it" instead of requiring emotional commitment
3. **Free Consulting:** Providing detailed solutions without budget confirmation
4. **Skipping Up-Front Contracts:** Assumptions about meeting objectives instead of explicit agreements
5. **Ignoring Disqualification Signals:** Continuing pursuit despite missing qualification criteria
6. **Money Discomfort:** Avoiding budget discussions due to personal money issues
7. **Prospect-Led Process:** Following prospect's system instead of Sandler's process
8. **No Permission to Say No:** Creating pressure instead of equal-stature conversation

## Resources

- Stage Inventory: `sample-data/Runtime/_Shared/knowledge/methodologies/Sandler/stage_inventory__Sandler.md`
- Adapter Config: `Framework/Methodologies/sandler.md`
- Source Materials: `sample-data/input/playbooks/methodologies/Sandler/`

## Provenance

created_by: convert_and_file
created_at: {{ISO_DATE}}
source_methodology: Sandler Selling System (Submarine Model)
source_materials: sample-data/input/playbooks/methodologies/Sandler/
