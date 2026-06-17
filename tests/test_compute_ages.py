import json

import yaml

import compute_ages as ca


def test_age_months_real_children():
    # June 2026 issue against the two real birth months.
    assert ca.age_months("2024-07", 2026, 6) == 23   # toddler, "approaching two"
    assert ca.age_months("2018-10", 2026, 6) == 92    # early elementary


def test_age_months_year_boundary():
    # January issue, birth month later in the prior years.
    assert ca.age_months("2024-07", 2025, 1) == 6
    assert ca.age_months("2018-10", 2026, 1) == 87


def test_stage_boundaries():
    s = ca.DEFAULT_STAGES
    assert ca.stage_for(11, s) == "infant"
    assert ca.stage_for(12, s) == "toddler"
    assert ca.stage_for(35, s) == "toddler"
    assert ca.stage_for(36, s) == "preschool"
    assert ca.stage_for(95, s) == "early elementary"
    assert ca.stage_for(96, s) == "middle childhood"
    assert ca.stage_for(23, s) == "toddler"
    assert ca.stage_for(92, s) == "early elementary"


def test_natural_age_is_honest_and_dayfree():
    a = ca.natural_age(23, False)
    assert "two" in a              # approaching two
    b = ca.natural_age(92, False)
    assert "seven" in b
    # Never claims days.
    for months in range(0, 216):
        assert "day" not in ca.natural_age(months, months % 12 == 0).lower()


def test_birth_month_edge_is_approximate():
    # Issue month == birth month -> ambiguous; flag it, don't claim a precise age.
    result = ca.compute(_profile(), None, "2025-07-10")  # younger child born 2024-07
    younger = next(c for c in result["children"] if c["id"] == "younger_child")
    assert younger["age_months"] == 12
    assert younger["birthday_this_month"] is True
    assert younger["approximate"] is True
    assert "about one" in younger["natural"]


def test_compute_integration(tmp_path):
    result = ca.compute(_profile(), None, "2026-06-16")
    by_id = {c["id"]: c for c in result["children"]}
    assert by_id["younger_child"]["stage"] == "toddler"
    assert by_id["older_child"]["stage"] == "early elementary"
    assert by_id["younger_child"]["birthday_this_month"] is False
    assert result["issue_date"] == "2026-06-16"


def test_active_context_filters_expired(tmp_path):
    ctx = tmp_path / "ctx.yaml"
    ctx.write_text(yaml.safe_dump({"context": [
        {"topic": "still active", "expires": "2026-12-01"},
        {"topic": "old news", "expires": "2026-01-01"},
        {"topic": "no expiry"},
    ]}))
    import datetime as dt
    active = ca.active_context(str(ctx), dt.date(2026, 6, 16))
    topics = {c["topic"] for c in active}
    assert "still active" in topics
    assert "no expiry" in topics
    assert "old news" not in topics


# --- helper ---------------------------------------------------------------

_PROFILE_CACHE = None


def _profile():
    """Write a temp profile with the real birth months once; return its path."""
    global _PROFILE_CACHE
    if _PROFILE_CACHE is None:
        import tempfile
        fd = tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False)
        yaml.safe_dump({"children": [
            {"id": "younger_child", "birth_month": "2024-07"},
            {"id": "older_child", "birth_month": "2018-10"},
        ]}, fd)
        fd.close()
        _PROFILE_CACHE = fd.name
    return _PROFILE_CACHE
