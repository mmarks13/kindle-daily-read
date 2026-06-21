# Semi-Supervised — project memory

A daily reading magazine about **family life, marriage, and fatherhood**, delivered as an
EPUB and read on Kindle. Subtitle: *Notes on being a dad.* Small, warm, literate, and
**never a burden to read** — a Sunday-magazine essay over coffee, not a parenting-news
digest or an advice feed. (The name is an ML pun: parenting is learning from mostly
unlabeled data with sparse guidance.)

## The two rules above all
- The goal is **not to maximize the children** — it's to help the family live well together.
- **Don't turn normal developmental variation into a problem** just to make an article.

## How it runs
- Orchestrated by `run_issue.sh`, intended for a nightly cron/launchd run.
- The writing step uses the **logged-in Claude Pro CLI** — do NOT set ANTHROPIC_API_KEY in
  the run environment (that switches to paid API billing). Only Kindle-email secrets are
  needed at runtime.
- Ages are always computed fresh from each child's **birth month** + the issue date; never
  copied from a past issue. Birth *day* is intentionally unknown, so ages are approximate
  (esp. during a birthday month) and prose never claims days.

## Editorial non-negotiables
- Every **non-fiction** piece is grounded in real sources that were actually opened, and
  links to them (inline on load-bearing claims + a per-chapter `**Sources:**` line).
  Never invent a study, number, quote, date, or URL.
- **Fiction** is allowed but must be labeled unmistakably (italic note containing *fiction*).
- Be careful with health/development/mental-health/marriage: never diagnose; distinguish
  normal variation from warning signs; say when a professional may help; explain framework
  disagreements instead of silently picking one; no guilt, no surveillance/manipulation
  framing, no fabricated family anecdotes.
- Personalize **topic selection**, not the prose. Child identifiers never appear in text.

## Map
- `.claude/skills/daily-issue/SKILL.md` — the daily editorial workflow + the masthead of
  eight writers (Iris, Theo, Dara, Nadia, Soren, Will, Cleo, Mira). Principle/feel-driven.
- `.claude/agents/source-researcher.md` — research subagent (watchlist + open web).
- `config/family_profile.yaml` (gitignored) — stable, sparse family facts; birth months.
  `config/family_profile.example.yaml` is the committed template.
- `config/recent_context.yaml` (gitignored) — temporary, auto-expiring circumstances.
- `config/sources.yaml` — curated, tiered source watchlist.
- `config/stages.yaml` — developmental-stage month boundaries (a soft aid, not a diagnosis).
- `scripts/compute_ages.py` — ages + stage + active context → JSON (the skill reads first).
- `scripts/check_issue.py` — hard pre-build gate (structure, bylines, word band, sources,
  fiction labels). `--check-links` optional, non-fatal.
- `scripts/make_epub.py` — markdown (`##` = chapters) → EPUB; embeds `assets/cover.png`.
- `scripts/update_history.py` — maintains `history.json` (45-day full detail + long-term
  rollup) and archives the issue into `issues/`. Holds the dedup helper `find_overlaps`.
- `scripts/send_to_kindle.py` — email the EPUB to Kindle (Gmail SMTP; `SENDER_EMAIL`,
  `KINDLE_EMAIL`, `GMAIL_APP_PASSWORD`).
- `history.json` — the magazine's memory; read before writing, committed so it persists.
- `issues/` — committed markdown + meta archive of what shipped. Built EPUBs in
  `docs/issues/` are gitignored.

## Run it
`bash run_issue.sh` → writes `out/issue.md` + `out/issue_meta.json`, validates, builds
`docs/issues/semi-supervised-DATE.epub`, records history, archives, and emails to Kindle.

## Tests
`pytest -q` — covers age math + birth-month edges, the validator, history update/compaction
+ dedup, and EPUB generation. Tests are offline (no network; link-checking is opt-in).
