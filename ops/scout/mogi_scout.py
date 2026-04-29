#!/usr/bin/env python3
"""
Mogi Scout — Playwright-based community scout
Scrapes public help/forum pages for automation fix opportunities.
Run: python3 mogi_scout.py
"""

import json
import os
import sys
import subprocess
from datetime import datetime

TARGETS = [
    {
        "name": "n8n Community Help",
        "url": "https://community.n8n.io/c/help/6",
        "type": "discourse",
        "selectors": {
            "posts": "a.title",
            "title_attr": "text",
        }
    },
    {
        "name": "Airtable Community - Ask the Community",
        "url": "https://community.airtable.com/t5/ask-the-community/bd-p/ask-the-community",
        "type": "khoros",
        "selectors": {}
    },
    {
        "name": "Reddit r/n8n",
        "url": "https://old.reddit.com/r/n8n/new/",
        "type": "reddit",
        "selectors": {}
    },
    {
        "name": "Reddit r/Airtable",
        "url": "https://old.reddit.com/r/Airtable/new/",
        "type": "reddit",
        "selectors": {}
    },
    {
        "name": "Reddit r/Zapier",
        "url": "https://old.reddit.com/r/Zapier/new/",
        "type": "reddit",
        "selectors": {}
    },
    {
        "name": "Reddit r/automation",
        "url": "https://old.reddit.com/r/automation/new/",
        "type": "reddit",
        "selectors": {}
    },
    {
        "name": "Make Community",
        "url": "https://community.make.com/c/help/5",
        "type": "discourse",
        "selectors": {}
    },
]


def scout_with_playwright():
    """Use Playwright CLI to scout each target."""
    results = []
    
    js_template = '''
const { chromium } = require('playwright');
(async () => {{
    const browser = await chromium.launch({{ headless: true }});
    const context = await browser.newContext({{
        userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }});
    const page = await context.newPage();
    
    try {{
        await page.goto('{url}', {{ waitUntil: 'networkidle', timeout: 30000 }});
        await page.waitForTimeout(3000);
        
        const posts = await page.evaluate(() => {{
            // Generic extraction — get links with titles
            const links = document.querySelectorAll('a');
            const results = [];
            const seen = new Set();
            
            for (const link of links) {{
                const href = link.href;
                const text = link.textContent.trim();
                if (!text || text.length < 10) continue;
                if (seen.has(text)) continue;
                seen.add(text);
                
                // Filter for post-like links
                if (href.includes('/t/') || href.includes('/topic/') || 
                    href.includes('reddit.com/r/') || href.includes('/comments/') ||
                    link.closest('[class*="topic"]') || link.closest('[class*="post"]') ||
                    link.closest('[class*="thread"]') || link.closest('article')) {{
                    results.push({{ title: text.substring(0, 200), url: href }});
                }}
            }}
            
            return results.slice(0, 30);
        }});
        
        console.log(JSON.stringify({{ source: '{name}', url: '{url}', posts: posts, error: null }}));
    }} catch (e) {{
        console.log(JSON.stringify({{ source: '{name}', url: '{url}', posts: [], error: e.message }}));
    }}
    
    await browser.close();
}})();
'''
    
    for target in TARGETS:
        js = js_template.format(name=target["name"], url=target["url"])
        tmp_js = f"/tmp/scout_{target['name'].replace(' ', '_').lower()[:20]}.js"
        
        with open(tmp_js, "w") as f:
            f.write(js)
        
        print(f"🔍 Scouting: {target['name']}...")
        try:
            result = subprocess.run(
                ["node", tmp_js],
                capture_output=True, text=True, timeout=45
            )
            # Parse JSON from stdout
            for line in result.stdout.strip().split('\n'):
                line = line.strip()
                if line.startswith('{'):
                    try:
                        data = json.loads(line)
                        results.append(data)
                        print(f"   Found {len(data.get('posts', []))} posts")
                    except json.JSONDecodeError:
                        print(f"   Could not parse output")
            if result.stderr:
                print(f"   stderr: {result.stderr[:200]}")
        except subprocess.TimeoutExpired:
            print(f"   ⏱ Timed out")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        os.remove(tmp_js)
    
    return results


def save_results(results):
    """Save scouted leads to JSON for processing."""
    output = {
        "scanned_at": datetime.now().isoformat(),
        "sources": results
    }
    
    path = "/Users/phillippreketes/mogi-automation-os/ops/scout/results.json"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(output, f, indent=2)
    
    # Also save a readable summary
    summary_path = "/Users/phillippreketes/mogi-automation-os/ops/scout/latest_scan.md"
    with open(summary_path, "w") as f:
        f.write(f"# Scout Results — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        all_posts = []
        for source in results:
            f.write(f"## {source['source']}\n")
            f.write(f"URL: {source['url']}\n")
            if source.get('error'):
                f.write(f"❌ Error: {source['error']}\n\n")
                continue
            f.write(f"Posts found: {len(source.get('posts', []))}\n\n")
            for post in source.get('posts', []):
                f.write(f"- [{post['title']}]({post['url']})\n")
                all_posts.append(source)
            f.write("\n")
    
    return path, summary_path


if __name__ == "__main__":
    print("=" * 50)
    print("MOGI SCOUT v1 — Headless Browser Scouting")
    print("=" * 50)
    
    results = scout_with_playwright()
    
    if results:
        json_path, md_path = save_results(results)
        print(f"\n✅ Results saved:")
        print(f"   JSON: {json_path}")
        print(f"   MD:   {md_path}")
    else:
        print("\n❌ No results. Check Playwright/Node setup.")
        sys.exit(1)
