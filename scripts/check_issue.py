#!/usr/bin/env python3
"""Hard pre-build gate for an issue. Fails (exit 1) if the issue violates the
editorial contract, so a bad issue can't be built or shipped.

Checks:
  - H1 is "Semi-Supervised"; a `<!-- mood: X -->` marker is present.
  - at least one `## ` chapter, each with a `*by <Name> — ...*` byline whose name
    is on the masthead.
  - total word count is within the day's band (weekday/Saturday/Sunday).
  - issue_meta.json is well-formed: has calculated_ages and one piece per chapter,
    titles aligned with the markdown.
  - every NON-FICTION piece has >=1 source in meta AND >=1 inline link in its prose.
  - every FICTION piece is labeled as fiction in its prose.

Link liveness is NOT checked by default (kept offline / fast). Pass --check-links to
HEAD-request each meta source; dead links are WARNINGS only, never fatal.

Usage:
    python scripts/check_issue.py --md out/issue.md --meta out/issue_meta.json
    python scripts/check_issue.py --md out/issue.md --meta out/issue_meta.json --check-links
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys

# Mirrors the masthead in .claude/skills/daily-issue/SKILL.md.
MASTHEAD = {"Iris", "Theo", "Dara", "Nadia", "Soren", "Will", "Cleo"}

# Inclusive word bands by day-of-week (Mon=0 ... Sun=6).
WORD_BANDS = {
    0: (2000, 2800), 1: (2000, 2800), 2: (2000, 2800), 3: (2000, 2800), 4: (2000, 2800),
    5: (4500, 6000),   # Saturday
    6: (3000, 4500),   # Sunday
}

MOOD_RE = re.compile(r"<!--\s*mood:\s*(.+?)\s*-->")
BYLINE_RE = re.compile(r"^\*by\s+([A-Za-z]+)\b.*\*\s*$", re.IGNORECASE)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def parse_chapters(md_text: str) -> list[dict]:
    """Return [{title, byline_name, body, links:[...], italics:[...]}] per `## ` chapter."""
    text = MOOD_RE.sub("", md_text)
    lines = text.splitlines()
    chapters: list[dict] = []
    cur = None
    for line in lines:
        if line.startswith("## "):
            cur = {"title": line[3:].strip(), "byline_name": None,
                   "body_lines": [], "italics": []}
            chapters.append(cur)
        elif cur is not None:
            stripped = line.strip()
            m = BYLINE_RE.match(stripped)
            if m and cur["byline_name"] is None:
                cur["byline_name"] = m.group(1).strip().title()
            elif stripped.startswith("*") and stripped.endswith("*") and len(stripped) > 2:
                cur["italics"].append(stripped.strip("*").strip())
            cur["body_lines"].append(line)
    for ch in chapters:
        body = "\n".join(ch["body_lines"])
        ch["body"] = body
        ch["links"] = LINK_RE.findall(body)
    return chapters


def word_count(md_text: str) -> int:
    return len(MOOD_RE.sub("", md_text).split())


def check(md_text: str, meta: dict, date: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    lines = md_text.splitlines()

    if not (lines and lines[0].strip() == "# Semi-Supervised"):
        errors.append('first line must be the H1 "# Semi-Supervised"')
    if not MOOD_RE.search(md_text):
        errors.append("missing mood marker <!-- mood: X -->")

    chapters = parse_chapters(md_text)
    if not chapters:
        errors.append("no `## ` chapters found")

    for ch in chapters:
        if ch["byline_name"] is None:
            errors.append(f'piece "{ch["title"]}" has no `*by <Name> — ...*` byline')
        elif ch["byline_name"] not in MASTHEAD:
            errors.append(f'piece "{ch["title"]}" byline "{ch["byline_name"]}" '
                          f"is not on the masthead")

    # Word band for the day.
    wd = dt.date.fromisoformat(date).weekday()
    lo, hi = WORD_BANDS[wd]
    wc = word_count(md_text)
    if not (lo <= wc <= hi):
        errors.append(f"word count {wc} outside the day's band {lo}-{hi}")

    # Meta structure.
    if not meta.get("calculated_ages"):
        errors.append("meta is missing calculated_ages")
    meta_pieces = meta.get("pieces", [])
    if len(meta_pieces) != len(chapters):
        errors.append(f"meta has {len(meta_pieces)} pieces but markdown has "
                      f"{len(chapters)} chapters")

    md_titles = {ch["title"] for ch in chapters}
    by_title = {ch["title"]: ch for ch in chapters}
    for p in meta_pieces:
        title = p.get("title", "")
        if title not in md_titles:
            errors.append(f'meta piece "{title}" has no matching markdown chapter')
            continue
        ch = by_title[title]
        if p.get("is_fiction"):
            labeled = any("fiction" in it.lower() for it in ch["italics"])
            if not labeled:
                errors.append(f'fiction piece "{title}" is not labeled as fiction '
                              f"(add an italic note, e.g. *A short fiction.*)")
        else:
            if not (p.get("sources") or []):
                errors.append(f'non-fiction piece "{title}" has no sources in meta')
            if not ch["links"]:
                errors.append(f'non-fiction piece "{title}" has no inline links in prose')

    return errors, warnings


def check_links(meta: dict) -> list[str]:
    import requests
    warnings = []
    seen = set()
    for p in meta.get("pieces", []):
        for url in p.get("sources", []) or []:
            if not url or url in seen:
                continue
            seen.add(url)
            try:
                r = requests.head(url, allow_redirects=True, timeout=10)
                if r.status_code >= 400:
                    r = requests.get(url, stream=True, timeout=10)
                if r.status_code >= 400:
                    warnings.append(f"link {url} returned {r.status_code}")
            except Exception as e:
                warnings.append(f"link {url} failed: {e}")
    return warnings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", default="out/issue.md")
    ap.add_argument("--meta", default="out/issue_meta.json")
    ap.add_argument("--date", help="issue date YYYY-MM-DD (default: from meta)")
    ap.add_argument("--check-links", action="store_true")
    args = ap.parse_args()

    with open(args.md) as f:
        md_text = f.read()
    with open(args.meta) as f:
        meta = json.load(f)
    date = args.date or meta.get("date")
    if not date:
        print("check_issue: no date given and none in meta", file=sys.stderr)
        return 1

    errors, warnings = check(md_text, meta, date)
    if args.check_links:
        warnings += check_links(meta)

    for w in warnings:
        print(f"WARNING: {w}", file=sys.stderr)
    if errors:
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        return 1

    print(f"check_issue: OK — {len(meta.get('pieces', []))} pieces, "
          f"{word_count(md_text)} words.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
