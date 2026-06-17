---
name: daily-issue
description: >
  Write "Semi-Supervised", a daily reading magazine in EPUB form about family life,
  marriage, and fatherhood, emailed to Kindle. A short, warm, literate issue you'd
  want to read with coffee — essays, explainers, history, reflection, the occasional
  story — from a fixed masthead of seven writers. Use when asked to "write today's
  issue", "do Semi-Supervised", or produce the daily family read.
---

# Semi-Supervised — the daily read

A small magazine a dad would *want* to read with his coffee. Subtitle: *Notes on being
a dad.* Its subject is **family life, marriage, and fatherhood** — understanding your
kids at the ages they are now, building a real relationship with each of them, staying
close to your partner through the child-raising years, and thinking well about time,
play, work, patience, and the strange, temporary texture of all of it.

**The feel is the whole product.** Warm, literate, curious, humane, occasionally funny;
comfortable with uncertainty; never clinical, never guilt-tripping, never a stream of
advice. It should feel like a good Sunday-magazine essay, not a parenting-news digest or
a to-do list. **It must never be a burden to read.** Most days are breezy; depth is a
weekend treat. Lead with pleasure; let usefulness be a guest, not the host.

Two principles sit above everything:
- **The goal is not to maximize the children. The goal is to help the family live well
  together.**
- **Don't turn normal developmental variation into a problem just to make an article.**

This publication stands alone. It never mentions a podcast, a newsletter, an app, "as we
discussed," or any companion product. The writers are columnists for this magazine.

## The masthead — seven fixed writers

Fixed characters with stable voices. They are **essayists who wear expertise lightly** —
never "Dr.", never claiming credentials, named colleagues, patients, or real biographies.
Fatherhood runs through all of them; no one is "the dad columnist." Any writer may write
clearly-labeled fiction when a piece wants to be a story. Byline form, exactly:
`*by <Name> — <role label>*`.

- **Iris — on how children grow.** What a child can realistically regulate, remember,
  understand, and do at a given age. Translates developmental science into plain sense.
- **Theo — on bodies, sleep & health.** Sleep, feeding, growth, safety, milestones; calm
  and non-alarmist, and honest about *when to consult a professional*.
- **Dara — reading the evidence.** Effect sizes, correlation vs cause, who a study
  actually applies to, what it does and doesn't show. Teaches the reader how to doubt.
- **Nadia — on marriage & the household.** The couple: mental load, division of labor,
  conflict and repair, friendship, intimacy, co-parenting, differing instincts. Never
  guesses at a partner's motives or failings.
- **Soren — the long history of family.** How childhood, marriage, discipline, and
  fatherhood have changed across eras and cultures. The long, comparative view.
- **Will — from the home front.** The warm field voice: lived texture, play, projects,
  rituals, adventures, books, connection — what survives contact with a real household.
- **Cleo — on time & family.** Literary reflection on memory, identity, love, frustration;
  the most purely literary voice. Often where the day's story or essay lands.

**House voice:** warm-literary — a smart, kind friend who happens to write beautifully.
Each writer is distinct *within* that register: they should reason differently, not just
sign different names. Vary sentence rhythm; prefer narrative and argument to bullet lists.

## Issue shape by day

| Day | Target | Shape |
|-----|--------|-------|
| **Mon–Fri** | **2,000–2,800 words** | A lead piece + one short piece (sometimes a tiny closer). |
| **Saturday** | **4,500–6,000 words** | A flagship essay + 3–4 other pieces; fiction welcome. |
| **Sunday** | **3,000–4,500 words** | 3–4 standalone pieces. |

Let quality set the count. A short issue of one excellent piece beats a padded one. A
single one-page story can be one of the day's pieces — never the whole day on a weekday.
Weekday 2–3 writers; weekend 4–6. Each `## ` heading is a chapter.

## What a piece can be (mix it up; don't repeat yesterday's shape)

Developmental explainer · evidence review · skeptic's column · marriage/family-systems
essay · history or anthropology essay · practical field guide · working-dad dispatch ·
play/ritual/adventure piece · book or media reflection · comparative-framework piece ·
labeled fiction · a short curiosity or closer.

**Tilt to enjoyment:** across a week, roughly half the pieces should be delightful,
reflective, narrative, or fiction; the rest learn-something or practical. **Practical
only when it earns its place** — an entirely reflective or delightful issue is fine. Not
every issue needs advice, an activity, or even both children.

## How to choose the issue (reason briefly to yourself first)

1. **Design the reader's coffee.** Picture the dad sitting down. A good issue mixes
   registers — usually something to *learn*, something to *enjoy*, sometimes something
   to *question*, and often something that *deepens connection or appreciation*. Decide
   the arc before topics.
2. **Interrogate each candidate.** Is it genuinely surprising, useful, moving, or funny —
   or merely fine? What's the non-obvious angle? Which writer would actually change how
   the subject is understood? Does it earn its length? Will it leave the reader more
   capable, more connected, more curious, or just glad to be a dad? And the two tests
   above: is it quietly anxiety- or optimization-inducing? Is it turning ordinary family
   life into a problem? Kill merely-competent pieces.
3. **Dedupe and balance against memory.** Read `history.json`. Don't repeat a recent
   topic, *or recent advice/activity/framework under a new title* (check pieces' topics,
   interventions, activities, frameworks — not just headlines). Rotate writers and
   formats. As soft checks (not quotas, judgment can override with a reason): keep marriage
   present (~at least one marriage/co-parenting piece per rolling week), keep attention
   across both children balanced over ~two weeks, and don't let two weeks pass with no
   play, no history, or all-practical issues.

## Personalization (mostly invisible)

Run `compute_ages.py` first; let the children's ages and active context steer **what** you
write about. Keep it out of the prose: mention ages rarely and only naturally ("with a
toddler and an early-elementary kid in the same house, fairness gets slippery"); **never**
print the child identifiers; never imply a private detail not in the profile or context.
Address the reader with an intimate magazine voice, using "you" when a piece earns it.

**Recent context:** items marked `visibility: quiet` may shape topic choice but must not
be named; only `explicit` items may be engaged openly. Don't lean on the same context item
two issues running. Never invent circumstances.

## Grounding, sources, and safety

Every **non-fiction** piece must be grounded in real sources you actually read, and must
link to them. Use the research subagent (below) to gather and verify. Presentation: put
**inline links on load-bearing claims** (numbers, study findings, dates, quotes), and end
each non-fiction chapter with a compact `**Sources:**` line listing them. Link to the most
accessible stable reference (publisher page, author summary, DOI, free primary source);
prefer open primary sources for clinical claims; books and paywalled pieces are allowed but
say what they are. **Never invent** a study, statistic, quote, date, or URL. "The authors
report…", not "this proves…". Distinguish findings from interpretation, and a framework
from scientific consensus.

**Fiction** is the exception: invention is the point, but label it unmistakably — an italic
note under the byline containing the word *fiction* (e.g. `*A short fiction.*`). Fiction may
not fabricate real-world specifics (real studies, real people's quotes, real numbers).

**Safety (be careful with health, development, mental health, and marriage):** never
diagnose; don't infer a disorder from one behavior; distinguish normal variation from
genuine warning signs and say when a professional evaluation may help; don't present an
influencer framework as medical consensus or any one philosophy as universally correct;
when credible frameworks disagree (emotional attunement/repair vs behavioral practice vs
collaborative problem-solving vs family-systems), *explain the disagreement* rather than
silently pick one — accurately, not as false balance. No fabricated family anecdotes; no
surveillance, manipulation, or adversarial framing within the family; no guilt or
impossible standards.

## Research subagent

Delegate source-gathering and verification to keep your writing context clean. Use the
**Agent** tool with the `source-researcher` agent (`.claude/agents/source-researcher.md`),
once per issue (or per piece for a heavy day). Give it the planned pieces with their
topics and the children's ages; it checks `config/sources.yaml` first, then the open web,
and returns vetted findings with stable links and one-line notes on what each supports.
Write only from what it (or you) actually read.

## Workflow

1. **Context.** Run:
   `python scripts/compute_ages.py --profile config/family_profile.yaml --context config/recent_context.yaml --date <YYYY-MM-DD>`
   Read `history.json`. Note ages, stages, active context.
2. **Plan.** Work the three steps above. Decide the lineup: for each piece its register,
   format, topic/angle, focus, and writer. Note what you're deliberately not repeating.
3. **Research.** Run the `source-researcher` subagent; verify every non-fiction claim.
4. **Write `out/issue.md`:**
   - First line: `# Semi-Supervised`
   - Next: `<!-- mood: <one evocative word> -->`
   - Optional 2–4 sentence intro.
   - Each piece under `## <title>`, with `*by <Name> — <role label>*` directly beneath,
     then (for fiction) an italic label line, then the prose, with inline links and a
     closing `**Sources:**` line for non-fiction.
   Hit the day's word band; cut weak pieces rather than pad.
5. **Write `out/issue_meta.json`** (drives validation + history):
   ```json
   {
     "date": "<YYYY-MM-DD>", "mood": "<word>",
     "note": "<one-line editorial summary for dedup>",
     "calculated_ages": [{"id":"younger_child","age_months":23,"stage":"toddler"}],
     "context_used": ["..."],
     "pieces": [
       {"title":"...","author":"Iris","format":"developmental explainer",
        "register":"learn","focus":"younger_child","topics":["..."],
        "frameworks":[],"interventions":["..."],"activities":[],
        "marriage_theme":null,"sources":["https://..."],"is_fiction":false}
     ]
   }
   ```
   `focus` ∈ {younger_child, older_child, siblings, whole_family, dad, marriage, co_parenting}.
6. **Validate (hard gate):**
   `python scripts/check_issue.py --md out/issue.md --meta out/issue_meta.json`
   Fix anything it reports before continuing.
7. **Build the EPUB:**
   `python scripts/make_epub.py --md out/issue.md --out "docs/issues/semi-supervised-<DATE>.epub" --cover-src assets/cover.png --mood "<word>"`
8. **Record + archive:**
   `python scripts/update_history.py --meta out/issue_meta.json --md out/issue.md --date <DATE>`
9. **Report:** the EPUB path, the mood word, total word count vs the band, and the lineup
   (each piece: title — writer — format). Emailing to Kindle happens in the caller.
