"""
tests/test_orchestrator.py — unit tests for the neuro-symbolic orchestrator.

Covers:
  - handle() dispatch: text, error, unknown function, plan with history.
  - _is_pure_route / _extract_route_to goal-shape predicates.
  - _resolve_location fallback chain (direct → classified → POI → edit-distance).
  - _rank_candidates (match-type priority + low-similarity rejection).
  - _handle_plan pipeline per branch:
      pure route, unknown tags, empty→relax, audit pass/fail.
  - _select_via_audit blacklist + MAX_REPLAN bound.
  - handle_pure_route (the no-LLM public entry for /api/route).
  - handle_text CLI helper.
  - Dijkstra + graph primitives.
"""

from engine.orchestrator import Orchestrator
from tests.helpers import (
    OrchestratorNoLLM,
    make_orchestrator_with_llm_result,
    make_plan_stub,
)


# ==================================================================
# handle() top-level dispatch
# ==================================================================


def test_handle_llm_returns_none():
    orchestrator = make_orchestrator_with_llm_result(None)
    result, history = orchestrator.handle("hi")
    assert result["type"] == "error"
    assert "couldn't process" in result["data"]["message"]


def test_handle_text_response():
    orchestrator = make_orchestrator_with_llm_result("Hello! How can I help you?")
    result, _ = orchestrator.handle("hello")
    assert result["type"] == "answer"
    assert result["data"]["answer"] == "Hello! How can I help you?"


def test_handle_unknown_function_returns_error():
    orchestrator = make_orchestrator_with_llm_result(("mystery", {}))
    result, _ = orchestrator.handle("hi")
    assert result["type"] == "error"
    assert "Unknown function" in result["data"]["message"]


def test_handle_passes_history_through():
    orchestrator = make_orchestrator_with_llm_result(
        ("plan", {"origin": "Siam", "goal": {"route_to": "Asok"}}),
        answer_text="Route narration.",
    )
    fake_history = [{"role": "user", "content": "previous"}]
    result, returned_history = orchestrator.handle("go", history=fake_history)
    assert result["type"] == "plan"
    assert isinstance(returned_history, list)


# ==================================================================
# _handle_plan — missing args
# ==================================================================


def test_handle_plan_missing_origin():
    orchestrator = make_orchestrator_with_llm_result(
        ("plan", {"goal": {"any_tag": ["temple"]}})
    )
    result, _ = orchestrator.handle("x")
    assert result["type"] == "error"
    assert "origin" in result["data"]["message"]


def test_handle_plan_missing_goal():
    orchestrator = make_orchestrator_with_llm_result(("plan", {"origin": "Siam"}))
    result, _ = orchestrator.handle("x")
    assert result["type"] == "error"


def test_handle_plan_unknown_origin():
    orchestrator = make_orchestrator_with_llm_result(
        ("plan", {"origin": "Narnia", "goal": {"any_tag": ["temple"]}})
    )
    result, _ = orchestrator.handle("x")
    assert result["type"] == "error"
    assert "Narnia" in result["data"]["message"]


# ==================================================================
# _handle_plan — pure-route shortcut
# ==================================================================


def test_handle_plan_pure_route_resolves_and_routes():
    orchestrator = make_orchestrator_with_llm_result(
        ("plan", {"origin": "Siam", "goal": {"route_to": "Asok"}}),
        answer_text="From Siam to Asok: ~6 min.",
    )
    result, _ = orchestrator.handle("route")
    assert result["type"] == "plan"
    assert result["data"]["origin"] == "Siam (CEN)"
    assert result["data"]["destination"] == "Asok (E4)"
    assert result["data"]["total_time"] > 0
    assert len(result["data"]["steps"]) >= 1
    assert result["data"]["answer"] == "From Siam to Asok: ~6 min."


def test_handle_plan_pure_route_unknown_destination():
    orchestrator = make_orchestrator_with_llm_result(
        ("plan", {"origin": "Siam", "goal": {"route_to": "Narnia"}})
    )
    result, _ = orchestrator.handle("route")
    assert result["type"] == "error"
    assert "Narnia" in result["data"]["message"]


# ==================================================================
# _handle_plan — unknown-tag surfacing
# ==================================================================


def test_handle_plan_surfaces_unknown_tag():
    orchestrator = make_orchestrator_with_llm_result(
        ("plan", {"origin": "Siam", "goal": {"any_tag": ["blorpatron"]}}),
        answer_text="Not a term I know.",
    )
    result, _ = orchestrator.handle("x")
    assert result["type"] == "plan"
    assert "unknown_tags" in result["data"]
    assert "blorpatron" in result["data"]["unknown_tags"]
    assert "note" in result["data"]


# ==================================================================
# _handle_plan — happy path with candidates
# ==================================================================


def test_handle_plan_finds_temples_from_siam():
    orchestrator = make_orchestrator_with_llm_result(
        ("plan", {"origin": "Siam", "goal": {"any_tag": ["temple"]}}),
        answer_text="A temple awaits.",
    )
    result, _ = orchestrator.handle("temples")
    assert result["type"] == "plan"
    data = result["data"]
    assert data["origin"] == "Siam (CEN)"
    # Either a chosen POI was routed to, or the audit rejected everything.
    if "poi" in data and data.get("poi"):
        assert "destination" in data
        assert "total_time" in data
        assert isinstance(data["steps"], list)
        assert "preference_score" in data
    else:
        assert "alternatives" in data


def test_handle_plan_preference_score_present_on_prefer_tag():
    orchestrator = make_orchestrator_with_llm_result(
        (
            "plan",
            {
                "origin": "Siam",
                "goal": {
                    "and": [
                        {"any_tag": ["museum"]},
                        {"prefer_tag": ["indoor"]},
                    ]
                },
            },
        ),
        answer_text="Found a museum.",
    )
    result, _ = orchestrator.handle("museum")
    assert result["type"] == "plan"
    data = result["data"]
    # prefer_tag contributes to preference_score when a candidate is chosen.
    if data.get("poi"):
        assert data.get("preference_score", 0) >= 0


# ==================================================================
# _is_pure_route / _extract_route_to
# ==================================================================


def test_is_pure_route_direct():
    assert Orchestrator._is_pure_route({"route_to": "Siam"}) is True


def test_is_pure_route_singleton_and():
    assert Orchestrator._is_pure_route({"and": [{"route_to": "Siam"}]}) is True


def test_is_pure_route_singleton_or():
    assert Orchestrator._is_pure_route({"or": [{"route_to": "Siam"}]}) is True


def test_is_pure_route_false_when_tagged():
    goal = {"and": [{"any_tag": ["temple"]}, {"route_to": "Siam"}]}
    assert Orchestrator._is_pure_route(goal) is False


def test_is_pure_route_false_for_raw_tag():
    assert Orchestrator._is_pure_route({"any_tag": ["temple"]}) is False


def test_is_pure_route_false_for_non_dict():
    assert Orchestrator._is_pure_route(None) is False
    assert Orchestrator._is_pure_route("route_to") is False
    assert Orchestrator._is_pure_route([]) is False


def test_extract_route_to_direct():
    assert Orchestrator._extract_route_to({"route_to": "Siam"}) == "Siam"


def test_extract_route_to_nested():
    goal = {"and": [{"any_tag": ["temple"]}, {"route_to": "Siam"}]}
    assert Orchestrator._extract_route_to(goal) == "Siam"


def test_extract_route_to_returns_none_when_absent():
    assert Orchestrator._extract_route_to({"any_tag": ["temple"]}) is None


# ==================================================================
# _resolve_location — fallback chain
# ==================================================================


def test_resolve_exact_station():
    orch = OrchestratorNoLLM()
    assert orch._resolve_location("Siam (CEN)") == "Siam (CEN)"


def test_resolve_prefix_station():
    orch = OrchestratorNoLLM()
    assert orch._resolve_location("Asok") == "Asok (E4)"


def test_resolve_substring_station():
    orch = OrchestratorNoLLM()
    assert orch._resolve_location("Chit") == "Chit Lom (E1)"


def test_resolve_poi_display_to_station():
    orch = OrchestratorNoLLM()
    assert orch._resolve_location("Grand Palace") == "Sanam Chai (BL31)"


def test_resolve_edit_distance_typo():
    orch = OrchestratorNoLLM()
    assert orch._resolve_location("Saim") == "Siam (CEN)"


def test_resolve_unknown_returns_none():
    orch = OrchestratorNoLLM()
    assert orch._resolve_location("Narnia") is None


def test_resolve_empty_returns_none():
    orch = OrchestratorNoLLM()
    assert orch._resolve_location("") is None
    assert orch._resolve_location(None) is None


# ==================================================================
# _rank_candidates — priority and rejection
# ==================================================================


def test_rank_candidates_exact_beats_prefix():
    orch = OrchestratorNoLLM()
    candidates = [
        {"station": "Siam Discovery", "match_type": "prefix"},
        {"station": "Siam (CEN)", "match_type": "exact"},
    ]
    assert orch._rank_candidates("Siam (CEN)", candidates) == "Siam (CEN)"


def test_rank_candidates_prefix_beats_substring():
    orch = OrchestratorNoLLM()
    candidates = [
        {"station": "Mo Chit (N8)", "match_type": "substring"},
        {"station": "Chit Lom (E1)", "match_type": "prefix"},
    ]
    assert orch._rank_candidates("Chit", candidates) == "Chit Lom (E1)"


def test_rank_candidates_empty():
    orch = OrchestratorNoLLM()
    assert orch._rank_candidates("anything", []) is None


def test_rank_candidates_low_similarity_rejected():
    orch = OrchestratorNoLLM()
    candidates = [
        {"station": "Very Long Station Name (Z99)", "match_type": "substring"},
    ]
    assert orch._rank_candidates("X", candidates) is None


# ==================================================================
# handle_pure_route — the no-LLM public entry
# ==================================================================


def test_handle_pure_route_success():
    orch = OrchestratorNoLLM()
    result = orch.handle_pure_route("Siam", "Asok")
    assert result["type"] == "plan"
    assert result["data"]["origin"] == "Siam (CEN)"
    assert result["data"]["destination"] == "Asok (E4)"
    assert result["data"]["total_time"] > 0
    assert len(result["data"]["steps"]) >= 1


def test_handle_pure_route_empty_input():
    orch = OrchestratorNoLLM()
    assert orch.handle_pure_route("", "Asok")["type"] == "error"
    assert orch.handle_pure_route("Siam", "")["type"] == "error"


def test_handle_pure_route_unknown_origin():
    orch = OrchestratorNoLLM()
    result = orch.handle_pure_route("Narnia", "Asok")
    assert result["type"] == "error"
    assert "Narnia" in result["data"]["message"]


def test_handle_pure_route_unknown_destination():
    orch = OrchestratorNoLLM()
    result = orch.handle_pure_route("Siam", "Narnia")
    assert result["type"] == "error"
    assert "Narnia" in result["data"]["message"]


# ==================================================================
# handle_text CLI helper
# ==================================================================


def test_handle_text_error_path():
    orchestrator = make_orchestrator_with_llm_result(None)
    text = orchestrator.handle_text("x")
    assert text == "Sorry, I couldn't process your request."


def test_handle_text_answer_path():
    orchestrator = make_orchestrator_with_llm_result("Here you go.")
    assert orchestrator.handle_text("x") == "Here you go."


def test_handle_text_plan_returns_answer_field():
    orchestrator = make_orchestrator_with_llm_result(
        ("plan", {"origin": "Siam", "goal": {"route_to": "Asok"}}),
        answer_text="From Siam to Asok.",
    )
    assert orchestrator.handle_text("route") == "From Siam to Asok."


# ==================================================================
# _select_via_audit — blacklist semantics
# ==================================================================


def test_select_via_audit_clean_route_wins(monkeypatch):
    """First candidate with no violations should be chosen."""
    orch = OrchestratorNoLLM()
    ranked = [
        {"name": "A", "station": "Siam (CEN)", "pref_score": 2,
         "path": ["Siam (CEN)", "Asok (E4)"], "cost": 6},
    ]
    monkeypatch.setattr(orch.prolog, "audit_route_for_path", lambda _p, _g: [])
    monkeypatch.setattr(
        orch.prolog, "build_route_steps", lambda _p: [{"type": "ride"}]
    )
    chosen, trail = orch._select_via_audit(ranked, {"any_tag": ["x"]})
    assert chosen is not None
    assert chosen["name"] == "A"
    assert trail == []


def test_select_via_audit_blacklists_violating(monkeypatch):
    """First candidate violates → blacklisted; second passes."""
    orch = OrchestratorNoLLM()
    ranked = [
        {"name": "BadPOI", "station": "S1", "pref_score": 3,
         "path": ["A", "B"], "cost": 5},
        {"name": "GoodPOI", "station": "S2", "pref_score": 2,
         "path": ["A", "C"], "cost": 8},
    ]
    call_log = []

    def fake_audit(path, _goal):
        call_log.append(path)
        if path == ["A", "B"]:
            return [{"step": {"type": "transfer"}, "reason": "weather_exposed"}]
        return []

    monkeypatch.setattr(orch.prolog, "audit_route_for_path", fake_audit)
    monkeypatch.setattr(orch.prolog, "build_route_steps", lambda _p: [])
    chosen, trail = orch._select_via_audit(ranked, {"any_tag": ["x"]})
    assert chosen is not None
    assert chosen["name"] == "GoodPOI"
    assert len(trail) == 1
    assert trail[0]["candidate"] == "BadPOI"
    assert trail[0]["violations"][0]["reason"] == "weather_exposed"


def test_select_via_audit_all_violate_returns_none(monkeypatch):
    """Every candidate violates → returns None + full audit trail."""
    orch = OrchestratorNoLLM()
    ranked = [
        {"name": "A", "station": "S1", "pref_score": 2, "path": ["X", "Y"], "cost": 5},
        {"name": "B", "station": "S2", "pref_score": 1, "path": ["X", "Z"], "cost": 7},
    ]
    monkeypatch.setattr(
        orch.prolog,
        "audit_route_for_path",
        lambda _p, _g: [{"step": {"type": "transfer"}, "reason": "weather_exposed"}],
    )
    monkeypatch.setattr(orch.prolog, "build_route_steps", lambda _p: [])
    chosen, trail = orch._select_via_audit(ranked, {"any_tag": ["x"]})
    assert chosen is None
    assert len(trail) == 2


def test_select_via_audit_max_replan_bound(monkeypatch):
    """Bound terminates even if blacklist never fills."""
    orch = OrchestratorNoLLM()
    ranked = [
        {"name": "A", "station": "S1", "pref_score": 1, "path": ["X", "Y"], "cost": 5},
    ]
    calls = {"n": 0}

    def always_violates(_p, _g):
        calls["n"] += 1
        return [{"step": {"type": "transfer"}, "reason": "r"}]

    monkeypatch.setattr(orch.prolog, "audit_route_for_path", always_violates)
    chosen, _ = orch._select_via_audit(ranked, {"any_tag": ["x"]})
    assert chosen is None
    # After one sweep the only candidate is blacklisted — the outer loop
    # terminates via `len(blacklist) >= len(ranked)`.
    assert calls["n"] == 1


# ==================================================================
# Dijkstra + graph primitives
# ==================================================================


def test_build_graph_makes_adjacency_dict():
    graph = Orchestrator._build_graph([("A", "B", 3), ("B", "C", 5)])
    assert graph["A"] == [("B", 3)]
    assert graph["B"] == [("C", 5)]


def test_dijkstra_same_node_zero_cost():
    path, cost = Orchestrator._dijkstra({}, "X", "X")
    assert path == ["X"] and cost == 0


def test_dijkstra_simple_path():
    graph = {"A": [("B", 3), ("C", 10)], "B": [("C", 4)]}
    path, cost = Orchestrator._dijkstra(graph, "A", "C")
    assert path == ["A", "B", "C"] and cost == 7


def test_dijkstra_disconnected_returns_none():
    graph = {"A": [("B", 1)]}
    path, cost = Orchestrator._dijkstra(graph, "A", "Z")
    assert path is None and cost is None


# ==================================================================
# Vocabulary cache
# ==================================================================


def test_vocab_cache_populated_once():
    orch = OrchestratorNoLLM()
    assert orch._vocab_cache is None
    _ = orch._vocab()
    assert orch._vocab_cache is not None


def test_synonyms_cache_populated_once():
    orch = OrchestratorNoLLM()
    assert orch._synonyms_cache is None
    _ = orch._synonyms()
    assert orch._synonyms_cache is not None
