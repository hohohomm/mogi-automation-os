# Mogi Automation OS

**Execution machine for marketplace service delivery.**

A complete operating system for discovering, quoting, building, delivering, and productising technical automation services — powered by Mogi (AI agent) + APIs/MCP.

---

## Three Service Lanes

### Lane 1: Python File Automation
Custom scripts that remove repetitive digital work. CSV processing, file renaming, data extraction, format conversion, report generation.

### Lane 2: Google Sheet / Spreadsheet Automation
Formula cleanup, Apps Script automation, dashboard builds, form-to-sheet workflows, status trackers, inventory systems.

### Lane 3: Workflow / API Automation (n8n → Zapier)
App-to-app connections: lead forms → CRM, email → sheets → notifications, document generation, AI-augmented workflows.

---

## System Components

| Component | Tool | Status |
|-----------|------|--------|
| Lead Tracker | Google Sheets / Airtable | ✅ Template ready |
| Client Intake | Tally / Google Forms | ✅ Template ready |
| Code Delivery | GitHub + local | ✅ Active |
| Workflow Engine | n8n | 🔧 Needs install |
| Payments | Stripe / PayID | 🔧 Needs account |
| Internal Classifier | Python script | ✅ Built |
| Proposal Library | Markdown prompts | ✅ Built |
| Delivery Templates | Markdown | ✅ Built |

---

## Quick Start

```bash
# Browse marketplaces (you do this)
# Find a job → paste into Mogi → get scored proposal

# Accept job → run:
python ops/classifier/bid_no_bid.py --description "job text here"

# Deliver using a script:
python scripts/python/file-automation/csv_cleaner.py --input client_file.csv

# Generate delivery:
# Use templates/templates/delivery/delivery_email.md
```

---

## Operating Docs

| File | Purpose |
|------|---------|
| `docs/SETUP.md` | Infrastructure setup guide |
| `docs/OPERATING_SYSTEM.md` | Full OS specification |
| `templates/intake/client_intake.md` | Questions to ask every client |
| `prompts/` | Mogi prompt library |
| `ops/lead-tracker/` | Score and track leads |
| `samples/` | Example deliverables |

---

**The goal is not to freelance forever. The goal is to find repeated paid requests, then productise the repeated part.**
