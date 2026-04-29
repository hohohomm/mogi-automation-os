#!/usr/bin/env python3
"""
File Organizer — Mogi Automation OS
Scans a directory and organizes files by type or date into subfolders.

Usage:
    python file_organizer.py --path ~/Downloads --by type
    python file_organizer.py --path ~/Desktop/mess --by date --dry-run

Modes:
    --by type   → Images/, Documents/, Audio/, Video/, Archives/, Code/, Other/
    --by date   → 2024/01-Jan/, 2024/02-Feb/, ...
"""

import argparse
import os
import shutil
import sys
from datetime import datetime
from collections import defaultdict
from pathlib import Path


# ── File type mapping ──────────────────────────────────────────────────────

FILE_TYPES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff", ".psd", ".ai"},
    "Documents": {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".odt", ".ods", ".odp", ".txt", ".rtf", ".md", ".csv", ".tsv"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma", ".aiff"},
    "Video": {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm", ".m4v"},
    "Archives": {".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar", ".tgz"},
    "Code": {".py", ".js", ".ts", ".html", ".css", ".json", ".xml", ".yaml", ".yml", ".sh", ".bash", ".sql", ".rb", ".go", ".rs", ".java", ".c", ".cpp", ".h", ".swift", ".kt"},
    "Spreadsheets": {".xlsx", ".xls", ".csv", ".numbers", ".ods"},
    "Applications": {".app", ".dmg", ".pkg", ".exe", ".msi", ".deb", ".rpm"},
    "Fonts": {".ttf", ".otf", ".woff", ".woff2", ".eot"},
}


def get_category(filename):
    ext = Path(filename).suffix.lower()
    for category, extensions in FILE_TYPES.items():
        if ext in extensions:
            return category
    if ext in ("", ".ds_store"):
        return None  # skip system files
    return "Other"


# ── Organization ───────────────────────────────────────────────────────────


def organize_by_type(source_dir, dry_run=False):
    """Move files into type-based folders."""
    stats = defaultdict(int)
    actions = []

    for entry in os.scandir(source_dir):
        if entry.is_dir():
            continue
        if entry.name.startswith("."):
            continue

        cat = get_category(entry.name)
        if cat is None:
            continue

        dest_dir = os.path.join(source_dir, cat)
        dest_path = os.path.join(dest_dir, entry.name)

        # Handle name collisions
        counter = 1
        while os.path.exists(dest_path):
            name, ext = os.path.splitext(entry.name)
            dest_path = os.path.join(dest_dir, f"{name}_{counter}{ext}")
            counter += 1

        actions.append((entry.path, dest_path, cat))
        stats[cat] += 1

    return actions, stats


def organize_by_date(source_dir, dry_run=False):
    """Move files into year/month folders based on modification time."""
    stats = defaultdict(int)
    actions = []

    for entry in os.scandir(source_dir):
        if entry.is_dir():
            continue
        if entry.name.startswith("."):
            continue

        mtime = os.path.getmtime(entry.path)
        dt = datetime.fromtimestamp(mtime)
        year_month = dt.strftime("%Y-%m")
        month_name = dt.strftime("%b")
        dest_dir = os.path.join(source_dir, dt.strftime("%Y"), f"{year_month}_{month_name}")
        dest_path = os.path.join(dest_dir, entry.name)

        counter = 1
        while os.path.exists(dest_path):
            name, ext = os.path.splitext(entry.name)
            dest_path = os.path.join(dest_dir, f"{name}_{counter}{ext}")
            counter += 1

        actions.append((entry.path, dest_path, year_month))
        stats[year_month] += 1

    return actions, stats


# ── Main ────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Organize files in a directory.")
    parser.add_argument("--path", "-p", required=True, help="Directory to organize")
    parser.add_argument("--by", "-b", choices=["type", "date"], default="type", help="Organization mode")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without moving")
    args = parser.parse_args()

    if not os.path.isdir(args.path):
        print(f"❌ Directory not found: {args.path}")
        sys.exit(1)

    if args.by == "type":
        actions, stats = organize_by_type(args.path, args.dry_run)
    else:
        actions, stats = organize_by_date(args.path, args.dry_run)

    if not actions:
        print("ℹ No files to organize.")
        return

    print(f"\n{'DRY RUN — ' if args.dry_run else ''}Organizing {len(actions)} files in: {args.path}\n")
    print("Breakdown:")
    for key, count in sorted(stats.items(), key=lambda x: -x[1]):
        print(f"  {key}: {count} files")

    print(f"\n{'Preview' if args.dry_run else 'Moving'} files...")
    for src, dst, label in actions:
        if args.dry_run:
            print(f"  [{label}] {os.path.basename(src)} → {os.path.relpath(dst, args.path)}")
        else:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(src, dst)
            print(f"  ✓ {os.path.basename(src)} → {os.path.relpath(dst, args.path)}")

    print(f"\n✅ {'Dry run complete' if args.dry_run else 'Done'} — {len(actions)} files organized.")


if __name__ == "__main__":
    main()
