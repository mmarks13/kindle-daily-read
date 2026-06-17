#!/usr/bin/env bash
# Generate today's Semi-Supervised issue end to end and email it to the Kindle.
# Intended for a nightly cron/launchd run. Each step that can fail without ruining
# the rest is non-fatal so a single hiccup doesn't lose the issue.
set -uo pipefail
cd "$(dirname "$0")"

DATE="$(date +%F)"
MODEL="${MODEL:-opus}"

# Load secrets (.env is gitignored). set -a exports everything sourced.
set -a; [ -f .env ] && . ./.env; set +a

# Activate the venv if present.
[ -f .venv/bin/activate ] && . .venv/bin/activate

echo "== Semi-Supervised $DATE =="

# Write the issue with the daily-issue skill. The skill computes ages, plans, runs the
# research subagent, writes out/issue.md + out/issue_meta.json, validates, builds the
# EPUB, and records history. Uses the logged-in Claude Pro CLI (no API key in env).
claude -p "Use the daily-issue skill to write today's issue of Semi-Supervised end to \
end, following its reasoning, grounding, and the day's length target. Build the EPUB with \
the cover and record the issue. Print the EPUB path when done." \
  --model "$MODEL" \
  --allowedTools "Bash Read Write WebSearch WebFetch Skill Agent" \
  --permission-mode acceptEdits \
  --max-turns 80 || echo "WARNING: issue generation failed"

EPUB="docs/issues/semi-supervised-$DATE.epub"

# Optional, non-fatal link liveness check on what shipped.
if [ -f out/issue_meta.json ]; then
  python scripts/check_issue.py --md out/issue.md --meta out/issue_meta.json \
    --check-links || echo "WARNING: link check reported problems (non-fatal)"
fi

# Email to Kindle (non-fatal; the EPUB still exists locally / in the archive).
if [ -f "$EPUB" ]; then
  python scripts/send_to_kindle.py --epub "$EPUB" \
    || echo "WARNING: Kindle email failed; EPUB still at $EPUB"
else
  echo "WARNING: no EPUB at $EPUB to send"
fi

echo "== done $DATE =="
