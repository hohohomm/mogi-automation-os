#!/usr/bin/env python3
"""
Data Extractor — Mogi Automation OS
Extract specific fields from messy data formats (CSV, PDF text, JSON, logs).

Usage:
    python data_extractor.py --input data.csv --output extracted.json --fields name,email,phone
    python data_extractor.py --input logfile.txt --pattern "ERROR:.*" --output errors.txt
"""

import argparse
import csv
import json
import os
import re
import sys
from pathlib import Path


def extract_from_csv(input_path, output_path, fields):
    """Extract specific columns from a CSV."""
    field_list = [f.strip() for f in fields.split(",")]
    extracted = []

    with open(input_path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        available = reader.fieldnames or []
        missing = [f for f in field_list if f not in available]
        if missing:
            print(f"⚠ Warning: fields not found: {', '.join(missing)}")

        for row in reader:
            extracted.append({f: row.get(f, "") for f in field_list if f in available})

    # Write output
    ext = Path(output_path).suffix.lower()
    if ext == ".json":
        with open(output_path, "w") as f:
            json.dump(extracted, f, indent=2)
    elif ext == ".csv":
        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[f for f in field_list if f in available])
            writer.writeheader()
            writer.writerows(extracted)
    else:
        with open(output_path, "w") as f:
            for item in extracted:
                f.write(json.dumps(item) + "\n")

    return len(extracted)


def extract_from_text(input_path, output_path, pattern):
    """Extract lines matching a regex pattern from a text file."""
    matches = []
    regex = re.compile(pattern)

    with open(input_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if regex.search(line):
                matches.append(line.rstrip())

    with open(output_path, "w") as f:
        f.write("\n".join(matches))

    return len(matches)


def main():
    parser = argparse.ArgumentParser(description="Extract specific data from files.")
    parser.add_argument("--input", "-i", required=True, help="Input file path")
    parser.add_argument("--output", "-o", required=True, help="Output file path")
    parser.add_argument("--fields", "-f", help="Comma-separated field names (for CSV)")
    parser.add_argument("--pattern", "-p", help="Regex pattern (for text/log files)")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"❌ File not found: {args.input}")
        sys.exit(1)

    ext = Path(args.input).suffix.lower()

    if ext == ".csv" and args.fields:
        count = extract_from_csv(args.input, args.output, args.fields)
        print(f"✅ Extracted {count} rows to {args.output}")
    elif args.pattern:
        count = extract_from_text(args.input, args.output, args.pattern)
        print(f"✅ Extracted {count} matching lines to {args.output}")
    else:
        print("❌ CSV files need --fields. Text files need --pattern.")
        sys.exit(1)


if __name__ == "__main__":
    main()
