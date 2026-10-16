"""Routing telemetry (item 6) — pure aggregation + roster validation.

The surface that makes "find the load-bearing skills, prune the long tail"
answerable from data instead of guessed. compute_routing is pure; the roster is
the canonical sub-skill set, so a typo'd skill name can't quietly fragment the
counts the way free-text would.
"""
import higgsfield_memory as hm


def _entry(eid, skills):
    return {"id": eid, "ts": "t", "skills": skills}


def test_validate_route_entry_accepts_roster_skills():
    real = sorted(hm.SUB_SKILLS)[:2]
    assert hm.validate_route_entry(_entry("R-001", real)) == []


def test_validate_route_entry_rejects_unknown_skill():
    problems = hm.validate_route_entry(_entry("R-001", ["higgsfield-prompt", "made-up"]))
    assert any("not in the sub-skill roster" in p and "made-up" in p for p in problems)


def test_validate_route_entry_rejects_empty_skills():
    assert any("non-empty list" in p
               for p in hm.validate_route_entry(_entry("R-001", [])))


def test_validate_route_entry_rejects_unknown_field():
    e = {**_entry("R-001", ["higgsfield-prompt"]), "bogus": 1}
    assert any("unknown field" in p for p in hm.validate_route_entry(e))


def test_compute_routing_counts_and_share():
    entries = [
        _entry("R-001", ["higgsfield-prompt", "higgsfield-camera"]),
        _entry("R-002", ["higgsfield-prompt", "higgsfield-seedance"]),
    ]
    r = hm.compute_routing(entries)
    assert r["n"] == 2
    by = {s["skill"]: s for s in r["skills"]}
    assert by["higgsfield-prompt"]["opens"] == 2
    assert by["higgsfield-prompt"]["pct"] == 1.0
    assert by["higgsfield-camera"]["opens"] == 1 and by["higgsfield-camera"]["pct"] == 0.5
    # ranked: prompt (2) before the 1-open skills
    assert r["skills"][0]["skill"] == "higgsfield-prompt"


def test_compute_routing_never_opened_is_the_tail():
    r = hm.compute_routing([_entry("R-001", ["higgsfield-prompt"])])
    assert "higgsfield-prompt" not in r["never_opened"]
    assert set(r["never_opened"]) == hm.SUB_SKILLS - {"higgsfield-prompt"}
    assert len(r["never_opened"]) == len(hm.SUB_SKILLS) - 1


def test_compute_routing_empty():
    r = hm.compute_routing([])
    assert r["n"] == 0 and r["skills"] == []
    assert set(r["never_opened"]) == hm.SUB_SKILLS


def test_seed_routing_log_is_schema_valid():
    import json
    from conftest import REPO
    db = json.loads((REPO / "db" / "routing-log.json").read_text(encoding="utf-8"))
    assert db["_total_entries"] == len(db["entries"])
    problems = []
    for e in db["entries"]:
        problems += hm.validate_route_entry(e)
    assert problems == []
