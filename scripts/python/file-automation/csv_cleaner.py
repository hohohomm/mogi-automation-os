#!/usr/bin/env python3
"""
CSV Cleaner — Mogi Automation OS
Takes a messy CSV export, infers types, sanitizes data, outputs clean file + summary report.

Usage:
    python csv_cleaner.py --input dirty.csv --output clean.csv [--delimiter ,] [--encoding utf-8]

Outputs:
    - clean.csv (sanitized data)
    - clean_report.txt (summary of changes made)
"""

import argparse
import csv
import sys
import os
import re
from datetime import datetime
from collections import Counter


# ── Column type inference ──────────────────────────────────────────────────

TYPES = {
    "empty": 0,
    "string": 1,
    "integer": 2,
    "float": 3,
    "date_ymd": 4,
    "date_dmy": 5,
    "date_mdy": 6,
    "boolean": 7,
    "email": 8,
    "phone": 9,
}


def infer_type(sample_values):
    """Heuristic column type detection from a sample of non-empty values."""
    if not sample_values:
        return "string"

    clean = [str(v).strip() for v in sample_values if v is not None and str(v).strip()]

    if not clean:
        return "string"

    # Check all match a type
    all_int = all(_is_integer(v) for v in clean)
    all_float = all(_is_float(v) for v in clean)
    all_bool = all(_is_boolean(v) for v in clean)
    all_date_ymd = all(_is_date_ymd(v) for v in clean)
    all_date_dmy = all(_is_date_dmy(v) for v in clean)
    all_email = all(_is_email(v) for v in clean)
    all_phone = all(_is_phone(v) for v in clean)

    if all_int:
        return "integer"
    if all_bool:
        return "boolean"
    if all_float:
        return "float"
    if all_date_ymd:
        return "date_ymd"
    if all_date_dmy:
        return "date_dmy"
    if all_email:
        return "email"
    if all_phone:
        return "phone"
    return "string"


def _is_integer(v):
    try:
        int(v.replace(",", ""))
        return True
    except (ValueError, AttributeError):
        return False


def _is_float(v):
    try:
        float(v.replace(",", "").replace("$", ""))
        return True
    except (ValueError, AttributeError):
        return False


def _is_boolean(v):
    return v.lower() in ("true", "false", "yes", "no", "y", "n", "1", "0")


_DATE_FORMATS = [
    ("%Y-%m-%d", "ymd"),
    ("%Y/%m/%d", "ymd"),
    ("%d/%m/%Y", "dmy"),
    ("%d-%m-%Y", "dmy"),
    ("%m/%d/%Y", "mdy"),
    ("%m-%d-%Y", "mdy"),
]


def _is_date_ymd(v):
    for fmt, kind in _DATE_FORMATS:
        if kind == "ymd":
            try:
                datetime.strptime(v, fmt)
                return True
            except ValueError:
                continue
    return False


def _is_date_dmy(v):
    for fmt, kind in _DATE_FORMATS:
        if kind == "dmy":
            try:
                datetime.strptime(v, fmt)
                return True
            except ValueError:
                continue
    return False


def _is_email(v):
    return bool(re.match(r"[^@\s]+@[^@\s]+\.[^@\s]+$", v))


def _is_phone(v):
    clean = re.sub(r"[\s\-\(\)\+]", "", v)
    return clean.isdigit() and 7 <= len(clean) <= 15


# ── Cleaning functions ─────────────────────────────────────────────────────


def clean_value(value, col_type):
    """Clean a single value based on its inferred type."""
    if value is None or str(value).strip() in ("", "N/A", "n/a", "NULL", "null", "None"):
        return None

    s = str(value).strip()

    if col_type == "integer":
        s = s.replace(",", "")
        try:
            return int(s)
        except ValueError:
            return s

    if col_type == "float":
        s = s.replace("$", "").replace(",", "").replace("€", "").replace("£", "")
        try:
            return round(float(s), 4)
        except ValueError:
            return s

    if col_type == "boolean":
        return s.lower() in ("true", "yes", "y", "1")

    if col_type.startswith("date_"):
        for fmt, kind in _DATE_FORMATS:
            if col_type.endswith(kind):
                try:
                    return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
                except ValueError:
                    continue
        return s

    return s


# ── Main ────────────────────────────────────────────────────────────────────


def clean_csv(input_path, output_path, delimiter=",", encoding="utf-8"):
    """Read dirty CSV, clean it, write clean CSV + report."""
    changes_log = {
        "rows_read": 0,
        "rows_written": 0,
        "empty_cells_filled": 0,
        "values_cleaned": 0,
        "duplicates_removed": 0,
        "columns": [],
        "warnings": [],
    }

    # Read
    with open(input_path, "r", encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        if not reader.fieldnames:
            raise ValueError("No columns found in CSV")
        rows = list(reader)

    changes_log["rows_read"] = len(rows)
    fieldnames = reader.fieldnames
    changes_log["columns"] = fieldnames

    # Infer types from first 100 non-empty rows
    sample_size = min(100, len(rows))
    col_types = {}
    for col in fieldnames:
        sample = [r.get(col) for r in rows[:sample_size] if r.get(col, "").strip()]
        col_types[col] = infer_type(sample)

    # Clean each row
    cleaned_rows = []
    for row in rows:
        cleaned = {}
        for col in fieldnames:
            raw = row.get(col, "")
            typed = clean_value(raw, col_types[col])
            if typed is None and raw.strip():
                changes_log["empty_cells_filled"] += 1
            if typed is not None and str(typed) != str(raw).strip():
                changes_log["values_cleaned"] += 1
            cleaned[col] = typed if typed is not None else ""
        cleaned_rows.append(cleaned)

    # Remove exact duplicate rows
    seen = set()
    deduped = []
    for row in cleaned_rows:
        key = tuple(row.items())
        if key not in seen:
            seen.add(key)
            deduped.append(row)
        else:
            changes_log["duplicates_removed"] += 1

    changes_log["rows_written"] = len(deduped)

    # Write clean CSV
    with open(output_path, "w", encoding=encoding, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(deduped)

    # Write report
    report_path = output_path.replace(".csv", "_report.txt")
    with open(report_path, "w") as f:
        f.write("=== CSV Cleaner Report ===\n")
        f.write(f"Input:  {os.path.basename(input_path)}\n")
        f.write(f"Output: {os.path.basename(output_path)}\n")
        f.write(f"Time:   {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(f"Rows read:     {changes_log['rows_read']}\n")
        f.write(f"Rows written:  {changes_log['rows_written']}\n")
        f.write(f"Duplicates removed: {changes_log['duplicates_removed']}\n\n")
        f.write("Inferred column types:\n")
        for col in fieldnames:
            f.write(f"  {col}: {col_types[col]}\n")
        f.write("\nWarnings:\n")
        if changes_log["warnings"]:
            for w in changes_log["warnings"]:
                f.write(f"  ⚠ {w}\n")
        else:
            f.write("  None\n")

    return changes_log, col_types


def main():
    parser = argparse.ArgumentParser(description="Clean a messy CSV file.")
    parser.add_argument("--input", "-i", required=True, help="Input CSV path")
    parser.add_argument("--output", "-o", default=None, help="Output CSV path (default: input_clean.csv)")
    parser.add_argument("--delimiter", "-d", default=",", help="CSV delimiter")
    parser.add_argument("--encoding", "-e", default="utf-8", help="File encoding")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"❌ File not found: {args.input}")
        sys.exit(1)

    output = args.output or args.input.replace(".csv", "_clean.csv")
    if output == args.input:
        output = args.input.replace(".csv", "_clean.csv")

    print(f"📂 Reading: {args.input}")
    log, types = clean_csv(args.input, output, args.delimiter, args.encoding)

    print(f"✅ Cleaned: {output}")
    print(f"📄 Report:  {output.replace('.csv', '_report.txt')}")
    print(f"\nSummary:")
    print(f"  Rows: {log['rows_read']} → {log['rows_written']}")
    print(f"  Duplicates removed: {log['duplicates_removed']}")
    print(f"  Values cleaned:     {log['values_cleaned']}")
    print(f"  Empty cells filled: {log['empty_cells_filled']}")


if __name__ == "__main__":
    main()
