"""
tests/test_audit_loop.py — audit/replan feedback loop.

The audit is where Prolog supervises Python: after Dijkstra picks the
cheapest route, the rulebook checks it for hard-constraint violations
and the orchestrator blacklists bad candidates and tries the next-best.

Three layers of tests here:

  1. Prolog rule: `step_violates/3` + `audit_route/3` catch
     weather_exposed and mobility_demanding violations.
  2. Wrapper: `PrologInterface.audit_route_for_path` returns the
     documented dict shape.
  3. Orchestrator: `_select_via_audit` blacklists violating candidates,
     returns None when every candidate violates, and is bounded by
     MAX_REPLAN.
"""

from engine.orchestrator import Orchestrator
from engine.prolog import PrologInterface
from tests.helpers import OrchestratorNoLLM


# ------------------------------------------------------------------
# Layer 1 — Prolog rule fires for open_air transfers.
# ------------------------------------------------------------------


class TestStepViolatesRule:
    def test_weather_exposed_fires_at_open_air_transfer(self):
        """Sanam Chai (BL31) is open_air — a transfer touching it violates
        none_tag([weather_exposed])."""
        p = PrologInterface()
        q = (
            "step_violates(transfer('Sanam Chai (BL31)', 'Silom (BL26)'), "
            "none_tag([weather_exposed]), R)"
        )
        results = list(p.prolog.query(q))
        assert results and results[0]["R"] == "weather_exposed"

    def test_weather_exposed_does_not_fire_for_covered_transfer(self):
        """Sukhumvit (BL22) ↔ Asok (E4) are both covered — no violation."""
        p = PrologInterface()
        q = (
            "step_violates(transfer('Sukhumvit (BL22)', 'Asok (E4)'), "
            "none_tag([weather_exposed]), R)"
        )
        assert list(p.prolog.query(q)) == []

    def test_mobility_demanding_fires_on_any_transfer(self):
        """Every transfer involves walking — mobility_demanding always fires."""
        p = PrologInterface()
        q = (
            "step_violates(transfer('Sukhumvit (BL22)', 'Asok (E4)'), "
            "none_tag([mobility_demanding]), R)"
        )
        results = list(p.prolog.query(q))
        assert results and results[0]["R"] == "mobility_demanding"

    def test_audit_route_aggregates_violations(self):
        """audit_route/3 collects all violations via findall."""
        p = PrologInterface()
        q = (
            "audit_route("
            "[transfer('Sanam Chai (BL31)', 'Silom (BL26)')], "
            "none_tag([weather_exposed]), V)"
        )
        results = list(p.prolog.query(q))
        assert len(results) == 1
        assert len(results[0]["V"]) == 1


# ------------------------------------------------------------------
# Layer 2 — Python wrapper returns the documented shape.
# ------------------------------------------------------------------


class TestAuditRouteForPath:
    def test_clean_route_returns_empty(self):
        p = PrologInterface()
        assert p.audit_route_for_path(
            ["Asok (E4)", "Phrom Phong (E5)"],
            {"none_tag": ["weather_exposed"]},
        ) == []

    def test_empty_path_returns_empty(self):
        p = PrologInterface()
        assert p.audit_route_for_path([], {"none_tag": ["weather_exposed"]}) == []

    def test_goal_with_no_audit_rules_returns_empty(self):
        """Goals with neither none_tag nor mobility_demanding don't audit."""
        p = PrologInterface()
        # any_tag alone shouldn't produce violations from the audit rules.
        assert p.audit_route_for_path(
            ["Asok (E4)", "Phrom Phong (E5)"],
            {"any_tag": ["temple"]},
        ) == []


# ------------------------------------------------------------------
# Layer 3 — Orchestrator's _select_via_audit feedback loop.
# ------------------------------------------------------------------


class TestSelectViaAudit:
    def test_first_clean_candidate_chosen(self, monkeypatch):
        orch = OrchestratorNoLLM()
        ranked = [
            {"name": "TempleA", "station": "Siam (CEN)", "pref_score": 2,
             "path": ["Siam (CEN)", "Asok (E4)"], "cost": 6},
            {"name": "TempleB", "station": "Silom (BL26)", "pref_score": 1,
             "path": ["Silom (BL26)", "Siam (CEN)"], "cost": 10},
        ]
        monkeypatch.setattr(orch.prolog, "audit_route_for_path", lambda _p, _g: [])
        monkeypatch.setattr(
            orch.prolog, "build_route_steps", lambda _p: [{"type": "ride"}]
        )
        chosen, trail = orch._select_via_audit(ranked, {"none_tag": ["weather_exposed"]})
        assert chosen is not None and chosen["name"] == "TempleA"
        assert trail == []

    def test_blacklist_advances_to_second(self, monkeypatch):
        orch = OrchestratorNoLLM()
        ranked = [
            {"name": "Bad", "station": "S1", "pref_score": 3,
             "path": ["X", "Y"], "cost": 5},
            {"name": "Good", "station": "S2", "pref_score": 2,
             "path": ["X", "Z"], "cost": 7},
        ]

        def fake_audit(path, _goal):
            if path == ["X", "Y"]:
                return [{"step": {"type": "transfer"}, "reason": "weather_exposed"}]
            return []

        monkeypatch.setattr(orch.prolog, "audit_route_for_path", fake_audit)
        monkeypatch.setattr(orch.prolog, "build_route_steps", lambda _p: [])
        chosen, trail = orch._select_via_audit(ranked, {"none_tag": ["x"]})
        assert chosen is not None and chosen["name"] == "Good"
        assert len(trail) == 1
        assert trail[0]["candidate"] == "Bad"

    def test_all_violate_returns_none_and_full_trail(self, monkeypatch):
        orch = OrchestratorNoLLM()
        ranked = [
            {"name": "A", "station": "S1", "pref_score": 2,
             "path": ["X", "Y"], "cost": 5},
            {"name": "B", "station": "S2", "pref_score": 1,
             "path": ["X", "Z"], "cost": 7},
        ]
        monkeypatch.setattr(
            orch.prolog,
            "audit_route_for_path",
            lambda _p, _g: [{"step": {"type": "transfer"}, "reason": "r"}],
        )
        chosen, trail = orch._select_via_audit(ranked, {"none_tag": ["x"]})
        assert chosen is None
        assert len(trail) == 2
        assert {t["candidate"] for t in trail} == {"A", "B"}

    def test_max_replan_bound_holds(self, monkeypatch):
        """MAX_REPLAN prevents infinite loops even if audit keeps rejecting."""
        orch = OrchestratorNoLLM()
        assert Orchestrator.MAX_REPLAN >= 1
        ranked = [
            {"name": "A", "station": "S1", "pref_score": 1,
             "path": ["X", "Y"], "cost": 5},
        ]
        call_count = {"n": 0}

        def counting_audit(_p, _g):
            call_count["n"] += 1
            return [{"step": {"type": "transfer"}, "reason": "r"}]

        monkeypatch.setattr(orch.prolog, "audit_route_for_path", counting_audit)
        chosen, _ = orch._select_via_audit(ranked, {"none_tag": ["x"]})
        assert chosen is None
        # With one candidate always violating, the outer loop exits after
        # one sweep via `len(blacklist) >= len(ranked)`. Bounded — not unbounded.
        assert call_count["n"] <= Orchestrator.MAX_REPLAN

    def test_empty_ranked_returns_none(self):
        orch = OrchestratorNoLLM()
        chosen, trail = orch._select_via_audit([], {"none_tag": ["x"]})
        assert chosen is None
        assert trail == []
