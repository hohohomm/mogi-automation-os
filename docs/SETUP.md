# Setup Guide

Infrastructure you need to get the Mogi Automation OS running.

## Step 1: Marketplace Profiles (10 min each)

| Platform | What to do | Estimated time |
|----------|------------|----------------|
| Upwork | Create profile, set hourly rate, add skills | 15 min |
| Fiverr | Create gig for each of the 3 lanes | 20 min |
| Airtasker | Create profile, list services | 10 min |

## Step 2: n8n (15 min)

n8n is the workflow engine. Run it locally with Docker.

```bash
# Pull and run n8n
docker run -d --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

Or use `docker compose` (recommended):

```yaml
# docker-compose.yml
version: '3.8'
services:
  n8n:
    image: n8nio/n8n
    ports:
      - "5678:5678"
    volumes:
      - ~/.n8n:/home/node/.n8n
    environment:
      - N8N_SECURE_COOKIE=false
```

Then open http://localhost:5678 and create an account.

## Step 3: Stripe (10 min)

1. Sign up at https://stripe.com
2. Get API keys from Developers → API keys
3. Save publishable key and secret key

Test mode is fine to start.

## Step 4: Lead Tracker (5 min)

Option A — Google Sheets:
1. Open Google Sheets
2. Create new spreadsheet
3. Copy headers from `ops/lead-tracker/lead_tracker_schema.md`
4. Name it "Lead Tracker"

Option B — Airtable:
1. Sign up at https://airtable.com
2. Create new base
3. Add fields matching the schema

## Step 5: Client Intake (5 min)

Option A — Tally.so:
1. Go to https://tally.so
2. Create form using questions from `templates/intake/client_intake.md`
3. Connect to your lead tracker

Option B — Google Forms:
1. Go to https://forms.google.com
2. Create form from the same questions
3. Link responses to your tracker sheet

## Step 6: Google Drive Template

Create this folder structure:

```
Clients/
  [Client Name]/
    Inputs/        ← Place client files here
    Outputs/       ← Deliverables go here
    Docs/          ← Notes, contracts, scope
    Archive/       ← Old versions, reference material
```

## Step 7: GitHub

The repo is already set up at https://github.com/hohohomm/mogi-automation-os

Clone locally:
```bash
cd ~/Desktop
git clone https://github.com/hohohomm/mogi-automation-os
```

## Step 8: Connect Mogi

Tell Mogi where everything lives. Mogi needs to know:
- Where the repo is cloned
- Where the lead tracker is (URL)
- Where client files go (Drive folder path)
- Stripe API keys (for generating payment links)
- n8n URL (for triggering workflows)

---

That's it. The rest is just: find jobs, deliver, track, repeat.
