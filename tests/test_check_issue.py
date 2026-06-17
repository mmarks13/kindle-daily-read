import check_issue as ci

DATE = "2026-06-16"  # a Tuesday -> weekday band 2000-2800


def build_md(words=2200, byline="*by Iris — on how children grow*",
             fiction_label=False, link=True, mood=True, h1=True):
    filler = " ".join(["word"] * words)
    parts = []
    if h1:
        parts.append("# Semi-Supervised")
    if mood:
        parts.append("<!-- mood: Holding -->")
    parts.append("## A Piece")
    parts.append(byline)
    if fiction_label:
        parts.append("*A short fiction.*")
    body = filler
    if link:
        body += " See [the source](https://example.com/study)."
    parts.append(body)
    return "\n".join(parts)


def base_meta(is_fiction=False, sources=None):
    if sources is None:
        sources = ["https://example.com/study"]
    return {
        "date": DATE,
        "calculated_ages": [{"id": "younger_child", "age_months": 23, "stage": "toddler"}],
        "pieces": [{
            "title": "A Piece", "author": "Iris", "is_fiction": is_fiction,
            "sources": sources,
        }],
    }


def test_valid_issue_passes():
    errors, _ = ci.check(build_md(), base_meta(), DATE)
    assert errors == [], errors


def test_missing_source_on_nonfiction_fails():
    errors, _ = ci.check(build_md(), base_meta(sources=[]), DATE)
    assert any("no sources" in e for e in errors)


def test_missing_inline_link_fails():
    errors, _ = ci.check(build_md(link=False), base_meta(), DATE)
    assert any("no inline links" in e for e in errors)


def test_unlabeled_fiction_fails():
    # Fiction in meta but no fiction label in prose.
    errors, _ = ci.check(build_md(fiction_label=False), base_meta(is_fiction=True), DATE)
    assert any("not labeled as fiction" in e for e in errors)


def test_labeled_fiction_passes_without_sources():
    md = build_md(fiction_label=True, link=False)
    errors, _ = ci.check(md, base_meta(is_fiction=True, sources=[]), DATE)
    assert errors == [], errors


def test_word_band_violation_fails():
    errors, _ = ci.check(build_md(words=500), base_meta(), DATE)
    assert any("outside the day's band" in e for e in errors)


def test_unknown_byline_fails():
    errors, _ = ci.check(build_md(byline="*by Bob — random guy*"), base_meta(), DATE)
    assert any("not on the masthead" in e for e in errors)


def test_missing_h1_and_mood_fail():
    errors, _ = ci.check(build_md(h1=False, mood=False), base_meta(), DATE)
    assert any("H1" in e for e in errors)
    assert any("mood" in e for e in errors)


def test_saturday_band_is_larger():
    # 2200 words is fine on a weekday but too short for Saturday (2026-06-20).
    errors, _ = ci.check(build_md(words=2200), base_meta(), "2026-06-20")
    assert any("outside the day's band" in e for e in errors)
