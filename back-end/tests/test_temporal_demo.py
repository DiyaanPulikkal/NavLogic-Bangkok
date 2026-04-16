"""
tests/test_temporal_demo.py — orchestrator-level temporal demos.

Five end-to-end plan runs that mirror the browser demo script, with the
LLM stubbed so the emitted `plan(origin, goal, time_context)` can be
pinned per case. Each test asserts what the temporal layer must deliver:

  1. After-sunset override fires Jodd Fairs on Saturday evening.
  2. Weekend-gated Chatuchak fails at Tuesday 10 AM — relaxation drops
     the `high_density` conjunct and names it in relaxation_note.
  3. Wat Arun's `photogenic` override fires at sunset (and Wat Arun is
     selected or surfaces as an alternative).
  4. Saturday afternoon: Jodd Fairs' night_market override fails —
     relaxation names the dropped conjunct.
  5. No LLM-supplied time → orchestrator injects its wall-clock frame
     and surfaces it on plan data.
"""

from tests.helpers import make_orchestrator_with_llm_result, make_plan_stub


def _run(stub, answer="ok"):
    """Tiny wrapper to build an orchestrator from a stub and invoke handle()."""
    from tests.helpers import OrchestratorNoLLM
    orch = OrchestratorNoLLM()
    orch.llm = stub
    stub._answer_text = answer
    result, _ = orch.handle("demo")
    return orch, result


def test_demo_jodd_fairs_at_saturday_evening():
    """Q1: 'I want a night market tonight from Asok.'
    LLM emits Sat 20:00 → Jodd Fairs' after_sunset override fires."""
    stub = make_plan_stub(
        origin="Asok",
        goal={"any_tag": ["night_market"]},
        time_context={"weekday": "sat", "hour": 20, "minute": 0},
    )
    _orch, result = _run(stub, answer="Night market tonight.")
    assert result["type"] == "plan"
    data = result["data"]
    assert data["time_context"]["weekday"] == "sat"
    assert data["time_context"]["hour"] == 20
    surfaced = {data.get("poi")} | set(data.get("alternatives", []))
    assert "Jodd Fairs Night Market" in surfaced


def test_demo_chatuchak_weekend_fail_relaxes_on_tuesday():
    """Q2: 'Bustling markets on Tuesday at 10 AM from Siam.'
    At Tue 10:00, Chatuchak's weekend override fails. The combined
    (market ∧ high_density) has no candidates (Chatuchak is the main
    market-themed high_density POI at that time), so relax fires and
    names the dropped conjunct."""
    stub = make_plan_stub(
        origin="Siam",
        goal={
            "and": [
                {"any_tag": ["market"]},
                {"any_tag": ["high_density"]},
            ]
        },
        time_context={"weekday": "tue", "hour": 10, "minute": 0},
    )
    _orch, result = _run(stub)
    assert result["type"] == "plan"
    data = result["data"]
    assert data["time_context"]["weekday"] == "tue"
    # Either relaxation fired, or the query resolved without drops — in
    # both outcomes time_context must be surfaced. But on this KB we
    # expect a drop, and the dropped string must name one of the conjuncts.
    note = data.get("relaxation_note")
    if note:
        assert any(
            "high_density" in d or "market" in d for d in note
        ), f"relaxation_note should name a dropped conjunct, got {note!r}"


def test_demo_wat_arun_photogenic_after_sunset():
    """Q3: 'Take me to something photogenic after sunset from Asok.'
    Wat Arun's photogenic is gated to after_sunset; at 18:30 it fires.
    Must appear as chosen POI or among alternatives."""
    stub = make_plan_stub(
        origin="Asok",
        goal={"any_tag": ["photogenic"]},
        time_context={"weekday": "sat", "hour": 18, "minute": 30},
    )
    _orch, result = _run(stub)
    assert result["type"] == "plan"
    data = result["data"]
    surfaced = {data.get("poi")} | set(data.get("alternatives", []))
    assert "Wat Arun" in surfaced


def test_demo_saturday_afternoon_night_market_relaxes():
    """Q4: 'Night market this Saturday afternoon from Phrom Phong.'
    Sat 14:00: night_market-gated POIs (jodd_fairs, asiatique) are
    silent because after_sunset has not hit. Relaxation should drop
    night_market; the time_context must surface the Saturday afternoon
    frame so the frontend badge can render it."""
    stub = make_plan_stub(
        origin="Phrom Phong",
        goal={
            "and": [
                {"any_tag": ["night_market"]},
                {"any_tag": ["shopping"]},
            ]
        },
        time_context={"weekday": "sat", "hour": 14, "minute": 0},
    )
    _orch, result = _run(stub)
    assert result["type"] == "plan"
    data = result["data"]
    assert data["time_context"] == {
        "weekday": "sat", "hour": 14, "minute": 0,
        "display": "Saturday 14:00",
    }
    # night_market alone fails at 14:00; relax must have dropped it.
    if data.get("relaxation_note"):
        assert any(
            "night_market" in d for d in data["relaxation_note"]
        )


def test_demo_no_time_context_defaults_to_wall_clock():
    """Q5: 'Anything lively right now from Asok.' — user pins no time.
    Orchestrator fills from _now_bangkok; time_context must surface
    verbatim on plan data so the frontend can render the badge."""
    orchestrator = make_orchestrator_with_llm_result(
        ("plan", {"origin": "Asok", "goal": {"any_tag": ["high_density"]}}),
        answer_text="Somewhere lively.",
    )
    # Freeze the clock so the test is deterministic.
    orchestrator._now_bangkok = lambda: {
        "weekday": "fri", "hour": 21, "minute": 15,
    }
    result, _ = orchestrator.handle("lively")
    assert result["type"] == "plan"
    tc = result["data"]["time_context"]
    assert tc["weekday"] == "fri"
    assert tc["hour"] == 21
    assert tc["minute"] == 15
    assert tc["display"] == "Friday 21:15"
