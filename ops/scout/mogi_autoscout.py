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
    },
    "make_community": {
        "url": "https://community.make.com/latest.json",
        "keywords": ["help", "error", "bug", "stuck", "webhook", "scenario", "module", "filter"]
    },
    "bubble_forum": {
        "url": "https://forum.bubble.io/latest.json",
        "keywords": ["help", "error", "bug", "stuck", "plugin", "api", "workflow"]
    },
    "webflow_forum": {
        "url": "https://discourse.webflow.com/latest.json",
        "keywords": ["help", "error", "bug", "cms", "code", "form", "not working"]
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


def scout_discourse(source_key):
    """Scout any Discourse forum via its JSON API."""
    leads = []
    config = TARGETS[source_key]
    url = config["url"]
    keywords = config["keywords"]

    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())

        for topic in data.get('topic_list', {}).get('topics', []):
            title = topic['title'].lower()
            if any(kw in title for kw in keywords):
                lead = {
                    "source": source_key,
                    "title": topic['title'],
                    "url": f"{url.replace('/latest.json', '') if url.endswith('/latest.json') else url.replace('/.json', '')}/t/{topic['slug']}/{topic['id']}",
                    "posts_count": topic['posts_count'],
                    "views": topic.get('views', 0),
                    "created": datetime.fromisoformat(topic['created_at'].replace('Z', '+00:00')).isoformat() if 'T' in str(topic['created_at']) else datetime.fromtimestamp(topic['created_at']).isoformat(),
                    "keyword": next((kw for kw in keywords if kw in title), None),
                }
                leads.append(lead)
    except Exception as e:
        print(f"  ⚠ {source_key}: {e}")

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

    # Scout all Discourse-based community forums
    discourse_sources = [k for k in TARGETS.keys() if k.endswith('_forum') or k.endswith('_community')]
    for source_key in discourse_sources:
        print(f"\n📡 Scouting {source_key}...")
        leads = scout_discourse(source_key)
        all_leads.extend(leads)
        print(f"   Found {len(leads)} leads")

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
