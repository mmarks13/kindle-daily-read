#!/usr/bin/env python3
"""Compute each child's approximate age and developmental stage for an issue date,
and return the currently-active recent-context items.

The daily-issue skill runs this FIRST, every issue, and reads the JSON. Ages are
always derived fresh from birth MONTH + issue date — never copied from a past issue.

Age is intentionally approximate. Because birth *day* is not stored:
    age_months = (issue_year - birth_year) * 12 + (issue_month - birth_month)
During the child's birth month the age is ambiguous (they may or may not have had
the birthday yet), so `birthday_this_month` is set and `approximate` is true; the
natural-language description leans on "about"/"approaching" and never claims days.

Usage:
    python scripts/compute_ages.py --profile config/family_profile.yaml \
        --context config/recent_context.yaml --date 2026-06-16
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys

import yaml

DEFAULT_STAGES = [
    {"name": "infant", "min": 0, "max": 11},
    {"name": "toddler", "min": 12, "max": 35},
    {"name": "preschool", "min": 36, "max": 59},
    {"name": "early elementary", "min": 60, "max": 95},
    {"name": "middle childhood", "min": 96, "max": 131},
    {"name": "preteen", "min": 132, "max": 155},
    {"name": "adolescence", "min": 156, "max": 215},
]

ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve"]


def _word(n: int) -> str:
    return ONES[n] if 0 <= n < len(ONES) else str(n)


def age_months(birth_month: str, year: int, month: int) -> int:
    by, bm = (int(x) for x in birth_month.split("-"))
    return (year - by) * 12 + (month - bm)


def stage_for(months: int, stages: list[dict]) -> str:
    for s in stages:
        if months <= s["max"]:
            return s["name"]
    return stages[-1]["name"] if stages else "beyond range"


def natural_age(months: int, birthday_this_month: bool) -> str:
    """An honest, day-free description: 'about two', 'seven and a half', 'approaching eight'."""
    if months < 0:
        return "not yet born"
    if months < 12:
        return f"{_word(months)} month{'s' if months != 1 else ''} old"
    years, rem = divmod(months, 12)
    # In the birth month the child is right at a year boundary — say "about N".
    if birthday_this_month or rem == 0:
        return f"about {_word(years)} year{'s' if years != 1 else ''} old"
    if rem <= 2:
        return f"just turned {_word(years)}"
    if 5 <= rem <= 7:
        return f"{_word(years)} and a half"
    if rem >= 10:
        return f"approaching {_word(years + 1)}"
    if rem < 5:
        return f"a little over {_word(years)}"
    return f"{_word(years)} and a half, heading toward {_word(years + 1)}"


def load_stages(path: str | None) -> list[dict]:
    if path and os.path.exists(path):
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        if data.get("stages"):
            return data["stages"]
    return DEFAULT_STAGES


def active_context(path: str | None, issue_date: dt.date) -> list[dict]:
    """Return context entries that have not expired as of the issue date."""
    if not path or not os.path.exists(path):
        return []
    with open(path) as f:
        data = yaml.safe_load(f) or {}
    out = []
    for item in data.get("context", []) or []:
        expires = item.get("expires")
        if expires:
            try:
                if dt.date.fromisoformat(str(expires)) < issue_date:
                    continue
            except ValueError:
                pass  # malformed date → keep it rather than silently drop
        out.append(item)
    return out


def compute(profile_path: str, context_path: str | None, date_str: str,
            stages_path: str | None = "config/stages.yaml") -> dict:
    issue_date = dt.date.fromisoformat(date_str)
    with open(profile_path) as f:
        profile = yaml.safe_load(f) or {}
    stages = load_stages(stages_path)

    children = []
    for child in profile.get("children", []) or []:
        bm = str(child.get("birth_month", "")).strip()
        months = age_months(bm, issue_date.year, issue_date.month)
        birthday_this_month = (int(bm.split("-")[1]) == issue_date.month)
        years, rem = divmod(months, 12) if months >= 0 else (0, 0)
        children.append({
            "id": child.get("id"),
            "birth_month": bm,
            "age_months": months,
            "age_years": years,
            "remainder_months": rem,
            "natural": natural_age(months, birthday_this_month),
            "stage": stage_for(months, stages),
            "birthday_this_month": birthday_this_month,
            "approximate": birthday_this_month,
        })

    return {
        "issue_date": date_str,
        "children": children,
        "active_context": active_context(context_path, issue_date),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="config/family_profile.yaml")
    ap.add_argument("--context", default="config/recent_context.yaml")
    ap.add_argument("--stages", default="config/stages.yaml")
    ap.add_argument("--date", required=True, help="issue date, YYYY-MM-DD")
    args = ap.parse_args()

    if not os.path.exists(args.profile):
        print(f"compute_ages: no profile at {args.profile} "
              f"(copy config/family_profile.example.yaml)", file=sys.stderr)
        return 1

    result = compute(args.profile, args.context, args.date, args.stages)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
