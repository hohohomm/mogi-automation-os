#!/usr/bin/env python3
"""
Lead scorer — runs against scouted results, produces scored leads.
"""

import json
from datetime import datetime

LEADS = [
    # r/n8n
    {"source": "reddit", "sub": "r/n8n", "title": "Cleaning messy incoming webhooks (names, phones) without a massive regex spaghetti workflow", "url": "https://reddit.com/r/n8n/comments/", "score_signals": ["clear problem", "tool stack clear", "narrow scope"], "red_flags": [], "score": 8},
    {"source": "reddit", "sub": "r/n8n", "title": "Need help to setup n8n through Docker", "url": "https://reddit.com/r/n8n/comments/", "score_signals": ["tool stack clear", "narrow scope"], "red_flags": ["probably free help"], "score": 5},
    {"source": "reddit", "sub": "r/n8n", "title": "I'm new and I can't use redis, HEELP", "url": "https://reddit.com/r/n8n/comments/", "score_signals": ["unresolved"], "red_flags": ["vague", "probably free help"], "score": 4},
    {"source": "reddit", "sub": "r/n8n", "title": "Shopify credential", "url": "https://reddit.com/r/n8n/comments/", "score_signals": [], "red_flags": ["vague"], "score": 2},
    # r/Airtable
    {"source": "reddit", "sub": "r/Airtable", "title": "FrankenTable rebuild. I just rebuilt 20+ tables and 100's of automations. OMG it's slow.", "url": "https://reddit.com/r/Airtable/comments/", "score_signals": ["clear problem", "mentions business context", "tool stack clear", "narrow scope"], "red_flags": [], "score": 9},
    {"source": "reddit", "sub": "r/Airtable", "title": "New Airtable user looking for experienced mentors with a blueprint to success", "url": "https://reddit.com/r/Airtable/comments/", "score_signals": ["tool stack clear", "unresolved"], "red_flags": ["vague", "free help"], "score": 4},
    {"source": "reddit", "sub": "r/Airtable", "title": "Filter a form based on logged in enterprise user? Can't find a work around.", "url": "https://reddit.com/r/Airtable/comments/", "score_signals": ["clear problem", "tool stack clear", "narrow scope", "unresolved"], "red_flags": [], "score": 7},
    {"source": "reddit", "sub": "r/Airtable", "title": "How to copy dropdown select lists to a new record?", "url": "https://reddit.com/r/Airtable/comments/", "score_signals": ["tool stack clear", "narrow scope"], "red_flags": [], "score": 6},
    {"source": "reddit", "sub": "r/Airtable", "title": "Sending multiple emails with automations and formulas, date based", "url": "https://reddit.com/r/Airtable/comments/", "score_signals": ["clear problem", "tool stack clear", "business context"], "red_flags": [], "score": 7},
    # r/Zapier
    {"source": "reddit", "sub": "r/Zapier", "title": "Where to find Zapier experts?", "url": "https://reddit.com/r/Zapier/comments/", "score_signals": ["directly asking for paid help", "mentions paid work"], "red_flags": [], "score": 10},
    {"source": "reddit", "sub": "r/Zapier", "title": "Full Sales Automation Setup: From Prospecting to Lead Follow-up (PerfexCRM + Zapier)", "url": "https://reddit.com/r/Zapier/comments/", "score_signals": ["tool stack clear", "business context"], "red_flags": ["likely too complex for $49"], "score": 6},
    {"source": "reddit", "sub": "r/Zapier", "title": "Slack automation workflows are getting way too complex to maintain as our team scales", "url": "https://reddit.com/r/Zapier/comments/", "score_signals": ["clear problem", "mentions business/team", "tool stack clear"], "red_flags": [], "score": 7},
    # n8n Community
    {"source": "n8n_forum", "sub": "n8n Community", "title": "Members cannot share workflows after upgrading to n8n 2.18.1 (admins unaffected)", "url": "https://community.n8n.io/", "score_signals": ["clear problem", "tool stack clear", "narrow scope", "unresolved"], "red_flags": [], "score": 8},
    {"source": "n8n_forum", "sub": "n8n Community", "title": "Need to Pass credential value dynamically at Same SQL Connection Name", "url": "https://community.n8n.io/", "score_signals": ["clear problem", "tool stack clear", "narrow scope"], "red_flags": [], "score": 7},
    {"source": "n8n_forum", "sub": "n8n Community", "title": "Been having issues since 2.0 version (BUGS?)", "url": "https://community.n8n.io/", "score_signals": ["unresolved"], "red_flags": ["vague"], "score": 4},
    {"source": "n8n_forum", "sub": "n8n Community", "title": "Execution data is written to the database even when it is disabled", "url": "https://community.n8n.io/", "score_signals": ["clear problem", "tool stack clear", "narrow scope"], "red_flags": [], "score": 7},
]

# Score
for lead in LEADS:
    base = lead["score"]
    negatives = len(lead["red_flags"]) * -3
    lead["final_score"] = max(0, base + negatives)

# Filter to 7+
high_value = [l for l in LEADS if l["final_score"] >= 7]
print(f"Total leads: {len(LEADS)}")
print(f"High-value (7+): {len(high_value)}\n")

print("=" * 60)
print("LEADS WORTH PURSUING (score ≥ 7)")
print("=" * 60)
for i, lead in enumerate(sorted(high_value, key=lambda x: -x["final_score"]), 1):
    print(f"\n{i}. 🎯 [{lead['final_score']}/10] {lead['title']}")
    print(f"   Source: {lead['source']}/{lead['sub']}")
    print(f"   Signals: {', '.join(lead['score_signals'])}")
    if lead['red_flags']:
        print(f"   ⚠️  {', '.join(lead['red_flags'])}")

# Save
output = {
    "generated": datetime.now().isoformat(),
    "total_leads": len(LEADS),
    "high_value_count": len(high_value),
    "leads": sorted(high_value, key=lambda x: -x["final_score"])
}
with open("/Users/phillippreketes/mogi-automation-os/ops/scout/scored_leads.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"\n✅ Saved to: ops/scout/scored_leads.json")
