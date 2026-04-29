# Mogi Automation OS — Operating System Specification

## Overview

This is the execution machine. Not a business plan. Not a pitch deck. An operating system for:
1. Discovering marketplace demand
2. Generating proposals
3. Building and delivering automation work
4. Tracking leads and outcomes
5. Detecting repeated requests → productising them

## Core Loop

```
Find job → Classify → Draft proposal → Client accepts
  → Intake form → Process → Package deliverable → Deliver
  → Follow up → Track outcome → Detect patterns → Productise repeats
```

## Components

### 1. Lead Discovery
- **Tool:** You browse marketplaces manually
- **Mogi role:** Classify jobs using `ops/classifier/bid_no_bid.py`
- **Output:** Decision (BID/MAYBE/PASS) + score + signals
- **Storage:** Lead tracker (Google Sheets or Airtable)

### 2. Proposal Generation
- **Tool:** Mogi drafts based on `templates/proposals/`
- **Human role:** You approve before sending
- **Rule:** Never auto-send proposals. Account safety first.

### 3. Client Intake
- **Tool:** Tally or Google Forms
- **Questions:** See `templates/intake/client_intake.md`
- **Connection:** n8n can auto-create Drive folder + lead tracker entry

### 4. Execution
- **Tool:** Local Python (scripts in `scripts/`)
- **Mogi role:** Generate code, test against sample data, package deliverable
- **Human role:** Verify results, protect client data, communicate

### 5. Delivery
- **Files:** GitHub repo (code) + Google Drive (files) + email (summary)
- **Templates:** `templates/delivery/`
- **Payment:** Stripe link or PayID before/after delivery

### 6. Follow-up
- **Schedule:** 3–7 days after delivery
- **Templates:** `templates/delivery/followup_template.md`
- **Purpose:** Testimonial, bug fixes, maintenance offer, repeat work

## Data Flow

```
Marketplace (Upwork/Fiverr/Airtasker)
  ↓ (you find job, paste to Mogi)
Mogi Classifier (bid_no_bid.py)
  ↓ (decision + score)
Lead Tracker (Google Sheets)
  ↓ (job accepted)
Intake Form (Tally)
  ↓ (client submits specs)
n8n → creates Drive folder + lead tracker entry + email notification
  ↓
Mogi generates deliverable (code / formulas / workflow)
  ↓
You test and approve
  ↓
Mogi packages delivery (README + files + delivery email)
  ↓
You send + process payment
  ↓
Follow-up (Mogi drafts, you send)
  ↓
Pattern detection → productisation?
```

## Expansion Path

| Stage | Revenue model | Automation level |
|-------|---------------|-----------------|
| 1. $49 gigs | Fixed price per job | Low (manual discovery, manual approval) |
| 2. Templates | Sell repeated script/workflow as template | Medium (Mogi generates from templates) |
| 3. Products | Gumroad / Etsy packs | High (automated delivery) |
| 4. Managed service | Monthly retainer for recurring automations | High (n8n + Mogi monitoring) |
| 5. SaaS | Charging for access to automation system | Full (but building phase) |

## Key Metrics to Track

- Jobs found per week
- BID rate / MAYBE rate / PASS rate
- Proposal acceptance rate
- Average fee per job
- Time per delivery
- Repeat client rate
- Repeated request patterns (→ product candidates)
