#!/usr/bin/env python3
"""
Bid / No-Bid Classifier — Mogi Automation OS
Scores a marketplace job description to decide if it's worth pursuing.

Usage:
    python bid_no_bid.py --description "Need a script to rename 500 PDF files"
    python bid_no_bid.py --description "Build me a full ecommerce platform for $50"
    python bid_no_bid.py --file job_description.txt
"""

import argparse
import json
import os
import sys
import re

# ── Scoring Factors ────────────────────────────────────────────────────────

FIT_SIGNALS = {
    "python": 3,
    "script": 3,
    "automation": 4,
    "workflow": 3,
    "csv": 2,
    "excel": 2,
    "google sheet": 3,
    "data": 2,
    "clean": 2,
    "format": 1,
    "convert": 2,
    "extract": 2,
    "scrape": 1,
    "file": 1,
    "rename": 1,
    "organize": 2,
    "report": 2,
    "dashboard": 3,
    "formula": 2,
    "zapier": 3,
    "n8n": 4,
    "api": 3,
    "integration": 3,
    "connect": 2,
    "migrate": 3,
    "sync": 3,
    "generate": 2,
    "worksheet": 3,
    "worksheet pack": 4,
    "study": 2,
    "practice": 2,
    "tutor": 2,
    "math": 2,
    "template": 2,
    "small script": 4,
    "simple script": 3,
}

RED_FLAGS = {
    "full stack": -2,
    "react": -1,
    "mobile app": -4,
    "ios": -4,
    "android": -4,
    "machine learning": -3,
    "deep learning": -5,
    "neural network": -5,
    "computer vision": -5,
    "enterprise": -2,
    "production grade": -2,
    "scalable": -1,
    "microservices": -3,
    "kubernetes": -4,
    "docker": -2,
    "devops": -3,
    "ecommerce platform": -2,
    "social media app": -4,
    "marketplace": -3,
    "crypto": -3,
    "blockchain": -5,
    "ai agent": -1,
    "llm": -1,
    "rag": -2,
    "scraping": -1,
    "illegal": -10,
}

URGENCY_SIGNALS = {
    "urgent": 3,
    "asap": 3,
    "today": 2,
    "tomorrow": 2,
    "this week": 1,
    "deadline": 1,
    "quick": 1,
    "simple": 1,
    "easy": 1,
}

# Budget regex patterns
BUDGET_PATTERNS = [
    (r"\$(\d+)[–-]\s*\$?(\d*)", "range"),
    (r"budget.*?(\d+)", "num"),
    (r"fixed.*?(\d+)", "num"),
    (r"\$(\d+)", "num"),
]


def extract_budget(text):
    """Try to extract budget range from text."""
    amounts = []
    for pattern, method in BUDGET_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            if isinstance(m, tuple):
                for v in m:
                    if v:
                        try:
                            amounts.append(int(v))
                        except ValueError:
                            pass
            else:
                try:
                    amounts.append(int(m))
                except ValueError:
                    pass
    if amounts:
        return min(amounts), max(amounts)
    return None, None


def classify_job(description):
    """Score a job description and return classification."""
    text = description.lower()
    words = text.split()

    score = 0
    signals = []
    warnings = []

    # Positive signals
    for keyword, weight in FIT_SIGNALS.items():
        if keyword in text:
            score += weight
            signals.append((keyword, weight, "fit"))

    # Red flags
    for keyword, weight in RED_FLAGS.items():
        if keyword in text:
            score += weight
            warnings.append((keyword, weight, "risk"))

    # Urgency
    urgency_score = 0
    for keyword, weight in URGENCY_SIGNALS.items():
        if keyword in text:
            urgency_score += weight
            signals.append((keyword, weight, "urgency"))

    # Budget
    min_budget, max_budget = extract_budget(text)

    # Length penalty — very long descriptions often mean scope creep
    if len(words) > 200:
        score -= 1
        warnings.append(("long description (scope creep risk)", -1, "risk"))

    # Length bonus — very short descriptions are easier
    if len(words) < 20:
        score += 1
        signals.append(("short description (focused)", 1, "fit"))

    # Classification
    if score >= 10:
                decision = "BID"
    elif score >= 5:
                decision = "MAYBE"
    else:
                decision = "PASS"

    # Make it a dict for pretty output
    result = {
        "decision": decision,
        "score": score,
        "urgency": urgency_score,
        "budget": f"${min_budget}" if min_budget else "Not mentioned",
        "budget_range": f"${min_budget}-${max_budget}" if min_budget and max_budget and min_budget != max_budget else None,
        "fit_signals": [s[0] for s in signals if s[2] == "fit"],
        "risks": [w[0] for w in warnings if w[2] == "risk"],
        "urgency_signals": [s[0] for s in signals if s[2] == "urgency"],
    }
    return result


def main():
    parser = argparse.ArgumentParser(description="Classify a marketplace job as BID/MAYBE/PASS.")
    parser.add_argument("--description", "-d", help="Job description text")
    parser.add_argument("--file", "-f", help="File containing job description")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.file:
        if not os.path.exists(args.file):
            print(f"❌ File not found: {args.file}")
            sys.exit(1)
        with open(args.file, "r") as f:
            description = f.read()
    elif args.description:
        description = args.description
    else:
        parser.print_help()
        sys.exit(1)

    result = classify_job(description)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    # Pretty output
    score_color = "🟢" if result["score"] >= 10 else "🟡" if result["score"] >= 5 else "🔴"
    print(f"\n{score_color} Decision: {result['decision']}")
    print(f"   Score: {result['score']} / urgency: +{result['urgency']}")
    print(f"   Budget: {result['budget']}")
    if result["budget_range"]:
        print(f"   Budget range: {result['budget_range']}")

    if result["fit_signals"]:
        print(f"\n   Fit signals: {', '.join(result['fit_signals'][:10])}")
    if result["risks"]:
        print(f"\n   ⚠  Risks: {', '.join(result['risks'][:5])}")
    if result["urgency_signals"]:
        print(f"\n   Urgency: {', '.join(result['urgency_signals'][:3])}")


if __name__ == "__main__":
    main()
