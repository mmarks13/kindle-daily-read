#!/usr/bin/env python3
"""Maintain the issue history: history.json.

The daily-issue skill READS this before writing each issue so it doesn't repeat
recent topics, advice, activities, frameworks, sources, formats, writers, or
emotional register, and so attention stays balanced across the children, marriage,
and the dad over time.

Unlike a title-only log, history records each piece's full editorial metadata from
the machine-readable out/issue_meta.json the skill emits. That lets the planner
detect "the same advice under a different title," not just a repeated headline.

Retention: the most recent KEEP_DAYS of issues are kept in full; older issues are
folded into a lightweight `rollup` (counts of topics/sources/frameworks/activities/
authors covered) so long-range memory survives without the file growing unbounded.

When --md is given, the issue's markdown and meta are also archived under issues/.

history.json:
{
  "issues": [ {date, mood, note, calculated_ages, context_used, pieces:[...]} ],  # newest-first
  "rollup": {topics:{}, sources:{}, frameworks:{}, activities:{}, authors:{},
             issues_compacted: int, oldest: "YYYY-MM-DD"},
  "updated": "YYYY-MM-DD"
}
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil

HISTORY_FILE = "history.json"
ARCHIVE_DIR = "issues"
ARCHIVE_PREFIX = "semi-supervised"
KEEP_DAYS = 45  # issues newer than this stay in full detail; older are compacted

# Per-piece metadata fields that feed the long-term rollup and dedup.
ROLLUP_FIELDS = ("topics", "frameworks", "activities")


def _bump(counter: dict, key, n: int = 1):
    if key:
        counter[key] = counter.get(key, 0) + n


def _empty_rollup() -> dict:
    return {"topics": {}, "sources": {}, "frameworks": {}, "activities": {},
            "authors": {}, "issues_compacted": 0, "oldest": None}


def fold_into_rollup(rollup: dict, issue: dict) -> None:
    """Accumulate one issue's metadata into the long-term rollup counts."""
    for piece in issue.get("pieces", []):
        _bump(rollup["authors"], piece.get("author"))
        for url in piece.get("sources", []) or []:
            _bump(rollup["sources"], url)
        for field in ROLLUP_FIELDS:
            for val in piece.get(field, []) or []:
                _bump(rollup[field], val)
    rollup["issues_compacted"] += 1
    date = issue.get("date")
    if date and (rollup["oldest"] is None or date < rollup["oldest"]):
        rollup["oldest"] = date


def find_overlaps(history: dict, candidate: dict,
                  fields=("topics", "interventions", "activities", "frameworks")) -> dict:
    """Dedup helper: for a candidate piece, return prior pieces in the full-detail
    history that share any topic/intervention/activity/framework. Catches repeated
    advice even when the title differs. Returns {field: [(date, title, value), ...]}."""
    out: dict[str, list] = {f: [] for f in fields}
    for issue in history.get("issues", []):
        for piece in issue.get("pieces", []):
            for f in fields:
                cand_vals = {str(v).strip().lower() for v in candidate.get(f, []) or []}
                for v in piece.get(f, []) or []:
                    if str(v).strip().lower() in cand_vals:
                        out[f].append((issue.get("date"), piece.get("title"), v))
    return out


def load_history() -> dict:
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            data = json.load(f)
        data.setdefault("issues", [])
        data.setdefault("rollup", _empty_rollup())
        return data
    return {"issues": [], "rollup": _empty_rollup()}


def update(meta: dict, date: str) -> dict:
    record = {
        "date": date,
        "mood": meta.get("mood", ""),
        "note": meta.get("note", ""),
        "calculated_ages": meta.get("calculated_ages", []),
        "context_used": meta.get("context_used", []),
        "pieces": meta.get("pieces", []),
    }

    data = load_history()
    # Idempotent: drop any existing record for this date, then prepend.
    data["issues"] = [i for i in data["issues"] if i.get("date") != date]
    data["issues"].insert(0, record)

    # Compact anything older than the retention window into the rollup.
    cutoff = (dt.date.fromisoformat(date) - dt.timedelta(days=KEEP_DAYS)).isoformat()
    kept, to_compact = [], []
    for issue in data["issues"]:
        (to_compact if issue.get("date", "") < cutoff else kept).append(issue)
    for issue in to_compact:
        fold_into_rollup(data["rollup"], issue)
    data["issues"] = kept
    data["updated"] = date
    return data


def archive(md_path: str, meta_path: str, date: str) -> None:
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    shutil.copyfile(md_path, os.path.join(ARCHIVE_DIR, f"{ARCHIVE_PREFIX}-{date}.md"))
    shutil.copyfile(meta_path, os.path.join(ARCHIVE_DIR, f"{ARCHIVE_PREFIX}-{date}.meta.json"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta", default="out/issue_meta.json")
    ap.add_argument("--md", help="issue markdown; if given, archived under issues/")
    ap.add_argument("--date", help="issue date YYYY-MM-DD (default: from meta)")
    args = ap.parse_args()

    with open(args.meta) as f:
        meta = json.load(f)
    date = args.date or meta.get("date")
    if not date:
        print("update_history: no date given and none in meta", flush=True)
        return 1

    data = update(meta, date)
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    if args.md:
        archive(args.md, args.meta, date)

    authors = ", ".join(dict.fromkeys(
        p.get("author", "") for p in meta.get("pieces", []) if p.get("author")))
    print(f"history: recorded {date} ({len(meta.get('pieces', []))} pieces; {authors}); "
          f"{len(data['issues'])} kept, {data['rollup']['issues_compacted']} compacted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
