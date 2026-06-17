# Semi-Supervised

A daily reading magazine about **family life, marriage, and fatherhood** — built as an
EPUB and emailed to a Kindle. Subtitle: *Notes on being a dad.*

It's meant to be short and genuinely enjoyable: a warm, literate Sunday-magazine essay
you'd read with coffee, not a parenting-news digest or an advice feed. Issues are written
by a fixed masthead of seven fictional columnists, grounded in real, linked sources, and
personalized by your children's ages — which are computed fresh each day from their birth
months, so the magazine always matches the kids you actually have right now.

The name is a small joke: parenting is *semi-supervised learning* — mostly unlabeled data,
sparse feedback, no ground truth, and you're the supervisor.

## How it works

```
compute ages  ─►  plan the issue  ─►  research (subagent)  ─►  write markdown + meta
      ─►  validate (hard gate)  ─►  build EPUB  ─►  record history  ─►  email to Kindle
```

The editorial brain is a Claude skill (`.claude/skills/daily-issue/SKILL.md`); the Python
scripts do the deterministic work around it (ages, validation, EPUB, history, delivery).

## Setup

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt          # plus: a system EPUB reader / Kindle

cp config/family_profile.example.yaml config/family_profile.yaml
cp config/recent_context.example.yaml config/recent_context.yaml   # optional
cp .env.example .env                       # fill in Kindle delivery secrets
```

Edit `config/family_profile.yaml` with each child's **birth month** (`YYYY-MM`) — never a
full birthday. Keep it sparse. Both real config files are gitignored.

### Kindle delivery
Set `SENDER_EMAIL`, `KINDLE_EMAIL`, and `GMAIL_APP_PASSWORD` in `.env`. `SENDER_EMAIL` must
be on your Amazon *Approved Personal Document E-mail List*; `GMAIL_APP_PASSWORD` is a Google
App Password for it. Delivery is non-fatal — a failed email never loses the issue.

## Generate an issue

```bash
bash run_issue.sh          # full nightly pipeline (writes, validates, builds, emails)
```

Or step through it manually:

```bash
python scripts/compute_ages.py --profile config/family_profile.yaml \
  --context config/recent_context.yaml --date 2026-06-16
# (write out/issue.md + out/issue_meta.json via the daily-issue skill)
python scripts/check_issue.py  --md out/issue.md --meta out/issue_meta.json
python scripts/make_epub.py    --md out/issue.md \
  --out docs/issues/semi-supervised-2026-06-16.epub --cover-src assets/cover.png
python scripts/update_history.py --meta out/issue_meta.json --md out/issue.md --date 2026-06-16
python scripts/send_to_kindle.py --epub docs/issues/semi-supervised-2026-06-16.epub
```

## Configuration

| File | What it controls |
|------|------------------|
| `config/family_profile.yaml` | Stable, sparse family facts; children's birth months. |
| `config/recent_context.yaml` | Temporary, auto-expiring circumstances that quietly steer topics. |
| `config/sources.yaml` | Curated, tiered source watchlist (research starts here). |
| `config/stages.yaml` | Developmental-stage month boundaries (a soft aid, never a diagnosis). |
| `.env` | Kindle-delivery secrets and `AUTHOR_NAME`. |

## Output & retention
- `out/issue.md`, `out/issue_meta.json` — working files (gitignored).
- `issues/semi-supervised-DATE.md` + `.meta.json` — committed archive of what shipped.
- `history.json` — rolling memory (45 days in full + a long-term rollup), committed.
- `docs/issues/*.epub` — built on demand and emailed; gitignored (not archived in git).

## Tests

```bash
pytest -q
```

Covers age math and birth-month edge cases, schema/validator behavior, history update +
compaction + dedup, and EPUB generation. Offline by default (link-checking is opt-in via
`check_issue.py --check-links`).

## Design notes
The full editorial and architectural rationale — masthead, feel, personalization,
grounding, safety, history/dedup — lives in `CLAUDE.md` and the skill file. This is a
standalone project; it shares ideas with, but no runtime dependency on, any other repo.
