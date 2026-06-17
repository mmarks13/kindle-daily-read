import json

import update_history as uh


def _meta(date, pieces=None):
    return {
        "date": date, "mood": "Holding", "note": "a note",
        "calculated_ages": [{"id": "younger_child", "age_months": 23, "stage": "toddler"}],
        "context_used": ["toddler is resisting bedtime"],
        "pieces": pieces or [{
            "title": "A Piece", "author": "Iris", "format": "essay", "register": "learn",
            "focus": "younger_child", "topics": ["bedtime"], "frameworks": ["RIE"],
            "interventions": ["a calm bedtime routine"], "activities": ["bath"],
            "marriage_theme": None, "sources": ["https://example.com/a"], "is_fiction": False,
        }],
    }


def _apply(meta, date, tmp_path):
    data = uh.update(meta, date)
    (tmp_path / "history.json").write_text(json.dumps(data))
    return data


def test_idempotent_same_date(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    _apply(_meta("2026-06-16"), "2026-06-16", tmp_path)
    data = _apply(_meta("2026-06-16"), "2026-06-16", tmp_path)
    same = [i for i in data["issues"] if i["date"] == "2026-06-16"]
    assert len(same) == 1


def test_newest_first(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    _apply(_meta("2026-06-15"), "2026-06-15", tmp_path)
    data = _apply(_meta("2026-06-16"), "2026-06-16", tmp_path)
    assert data["issues"][0]["date"] == "2026-06-16"


def test_rich_fields_persist(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    data = _apply(_meta("2026-06-16"), "2026-06-16", tmp_path)
    rec = data["issues"][0]
    assert rec["calculated_ages"][0]["stage"] == "toddler"
    assert rec["context_used"] == ["toddler is resisting bedtime"]
    assert rec["pieces"][0]["interventions"] == ["a calm bedtime routine"]
    assert rec["pieces"][0]["focus"] == "younger_child"


def test_old_issue_compacted_into_rollup(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    old = {
        "issues": [{
            "date": "2026-01-01", "mood": "x", "note": "", "calculated_ages": [],
            "context_used": [],
            "pieces": [{
                "author": "Iris", "topics": ["screens"], "frameworks": ["RIE"],
                "activities": ["walk"], "sources": ["https://old.example/x"],
            }],
        }],
        "rollup": uh._empty_rollup(),
    }
    (tmp_path / "history.json").write_text(json.dumps(old))

    data = uh.update(_meta("2026-06-16"), "2026-06-16")
    dates = [i["date"] for i in data["issues"]]
    assert "2026-01-01" not in dates              # compacted out of full detail
    assert "2026-06-16" in dates                  # recent kept
    assert data["rollup"]["issues_compacted"] == 1
    assert data["rollup"]["topics"]["screens"] == 1
    assert data["rollup"]["authors"]["Iris"] == 1


def test_find_overlaps_detects_repeated_advice():
    history = {"issues": [{
        "date": "2026-06-10",
        "pieces": [{"title": "An Old Headline",
                    "interventions": ["visual bedtime schedule"],
                    "topics": ["bedtime"]}],
    }]}
    candidate = {"title": "A Totally Different Headline",
                 "interventions": ["Visual Bedtime Schedule"],   # same advice, new title, diff case
                 "topics": ["mealtime"]}
    overlaps = uh.find_overlaps(history, candidate)
    assert overlaps["interventions"]        # caught despite the new title
    assert not overlaps["topics"]           # bedtime vs mealtime: no overlap
