#!/usr/bin/env python3
"""
Mogi Auto-Scout — Continuous lead discovery script.
Run this periodically (cron every 4-6h) to find new leads.

Usage:
    python3 mogi_autoscout.py          # Full scout
    python3 mogi_autoscout.py --quick  # Only top 5 sources
"""

import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime
from collections import defaultdict

HEADERS = {'User-Agent': 'MogiScout/1.0'}

# ── Sources ────────────────────────────────────────────────────────────────

TARGETS = {
    "reddit": {
        "subreddits": {
            "r/n8n": ["help", "webhook", "error", "workflow", "stuck", "bug"],
            "r/Airtable": ["help", "formula", "automation", "stuck", "workflow", "sync"],
            "r/Zapier": ["help", "not working", "error", "expert", "connect"],
            "r/automation": ["workflow", "automation", "n8n", "Zapier", "stuck"],
            "r/Entrepreneur": ["automation", "workflow", "Zapier", "Airtable"],
        },
        "search_terms": [
            "need someone to build",
            "can I pay someone",
            "stuck with automation",
            "automation help",
            "workflow help",
            "Zapier help",
            "n8n help",
            "Airtable formula",
            "webhook issue",
            "API integration",
        ]
    },
    "n8n_forum": {
        "url": "https://community.n8n.io/latest.json",
        "keywords": ["help", "error", "bug", "issue", "stuck", "workflow", "webhook"]
    }
}


# ── Scouting ───────────────────────────────────────────────────────────────


def scout_reddit():
    """Scout Reddit for leads."""
    leads = []
    now = datetime.now()
    cutoff = now.timestamp() - (7 * 86400)  # 7 days back

    for subreddit, keywords in TARGETS["reddit"]["subreddits"].items():
        sub_name = subreddit.replace("r/", "")
        for keyword in keywords[:2]:  # 2 keywords per subreddit to be efficient
            encoded = urllib.parse.quote(keyword)
            url = f"https://www.reddit.com/r/{sub_name}/search.json?q={encoded}&restrict_sr=on&sort=new&limit=5"
            try:
                req = urllib.request.Request(url, headers=HEADERS)
                with urllib.request.urlopen(req, timeout=10) as r:
                    data = json.loads(r.read())

                for child in data['data']['children']:
                    d = child['data']
                    created = d.get('created_utc', 0)
                    if created < cutoff:
                        continue

                    lead = {
                        "source": f"r/{sub_name}",
                        "title": d['title'],
                        "url": f"https://reddit.com{d['permalink']}",
                        "score": d['score'],
                        "comments": d['num_comments'],
                        "created": datetime.fromtimestamp(created).isoformat(),
                        "body": d.get('selftext', '')[:300],
                        "keyword": keyword,
                    }
                    leads.append(lead)
            except Exception as e:
                print(f"  ⚠ r/{sub_name} [{keyword}]: {e}")
                continue

    return leads


def scout_n8n_forum():
    """Scout the n8n Discourse forum via API."""
    leads = []
    url = TARGETS["n8n_forum"]["url"]
    keywords = TARGETS["n8n_forum"]["keywords"]

    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())

        for topic in data.get('topic_list', {}).get('topics', []):
            title = topic['title'].lower()
            # Only grab if it matches a help keyword
            if any(kw in title for kw in keywords):
                lead = {
                    "source": "n8n_forum",
                    "title": topic['title'],
                    "url": f"https://community.n8n.io/t/{topic['slug']}/{topic['id']}",
                    "posts_count": topic['posts_count'],
                    "views": topic.get('views', 0),
                    "created": datetime.fromtimestamp(topic['created_at']).isoformat(),
                }
                leads.append(lead)
    except Exception as e:
        print(f"  ⚠ n8n forum: {e}")

    return leads


# ── Main ────────────────────────────────────────────────────────────────────


def main():
    print("=" * 50)
    print("MOGI AUTO-SCOUT")
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S AEST"))
    print("=" * 50)

    all_leads = []

    print("\n📡 Scouting Reddit...")
    reddit_leads = scout_reddit()
    all_leads.extend(reddit_leads)
    print(f"   Found {len(reddit_leads)} leads")

    print("\n📡 Scouting n8n forum...")
    n8n_leads = scout_n8n_forum()
    all_leads.extend(n8n_leads)
    print(f"   Found {len(n8n_leads)} leads")

    # Deduplicate by URL
    seen = set()
    unique = []
    for lead in all_leads:
        if lead['url'] not in seen:
            seen.add(lead['url'])
            unique.append(lead)

    # Save
    output = {
        "scanned_at": datetime.now().isoformat(),
        "total_raw": len(all_leads),
        "total_unique": len(unique),
        "leads": unique,
    }

    os.makedirs("results", exist_ok=True)
    path = f"results/scan_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n✅ Saved {len(unique)} unique leads to {path}")

    # Group by source
    by_source = defaultdict(list)
    for lead in unique:
        by_source[lead['source']].append(lead)

    print("\n📊 Summary by source:")
    for source, items in sorted(by_source.items()):
        print(f"   {source}: {len(items)} leads")
        for item in items[:3]:
            print(f"     · [{item.get('score', '?')}] {item['title'][:70]}")
        if len(items) > 3:
            print(f"     ... and {len(items) - 3} more")

    return path


if __name__ == "__main__":
    main()
