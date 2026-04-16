"""
tests/helpers.py — test-only fixtures wiring the orchestrator without the LLM.

Keeps integration tests LLM-free (no network, no API key needed) by
swapping in StubLLM for real Gemini calls. Two public constructors:

  OrchestratorNoLLM()          — fully-constructed orchestrator, llm=None.
                                 Use for direct unit tests of internals.
  make_orchestrator_with_llm_result(result, answer=None)
                               — orchestrator whose translate_to_query
                                 returns `result` and whose format_result
                                 fills data.answer with `answer`.

Also exported:
  StubLLM      — conforms to the new LLMInterface contract (4-arg signature).
  make_plan_stub(origin, goal, answer=None)
               — shorthand: returns a StubLLM emitting plan(origin=..., goal=...).
  build_graph_and_weights(edges) — shared adjacency-dict builder for exhaustive
                                   route tests.
"""

from engine.orchestrator import Orchestrator
from engine.prolog import PrologInterface

# Neutral wall-clock for non-temporal tests: Wednesday, 12:00 PM.
# No active_tag/3 override fires at this frame (after_sunset, weekend,
# late_night, friday_evening all fail), so existing specs behave
# identically to the pre-temporal-layer world.
DEFAULT_TIME_CTX = {"weekday": "wed", "hour": 12, "minute": 0}


class OrchestratorNoLLM(Orchestrator):
    """Orchestrator with llm=None; Prolog loaded from the real KB."""

    def __init__(self):
        self.llm = None
        self.prolog = PrologInterface()
        self._vocab_cache = None
        self._synonyms_cache = None


class StubLLM:
    """Stub LLM matching the new `LLMInterface` surface.

    `translate_to_query` returns the pre-configured result; `format_result`
    injects `answer_text` into `data.answer` so the orchestrator's
    `_format` step is covered without hitting Gemini.
    """

    def __init__(self, result, answer_text: str | None = None):
        self._result = result
        self._answer_text = answer_text
        self.last_time_hint: dict | None = None

    def translate_to_query(
        self, user_input, history=None, vocab=None, synonyms=None, time_hint=None,
    ):
        if history is None:
            history = []
        self.last_time_hint = time_hint
        return self._result, history

    def format_result(self, result, history=None, vocab=None, synonyms=None):
        if history is None:
            history = []
        result.setdefault("data", {})["answer"] = self._answer_text
        return result, history


def make_orchestrator_with_llm_result(result, answer_text: str | None = None):
    """Build a fully-wired OrchestratorNoLLM whose LLM is the given stub."""
    orchestrator = OrchestratorNoLLM()
    orchestrator.llm = StubLLM(result, answer_text)
    return orchestrator


def make_plan_stub(
    origin: str, goal: dict, answer_text: str | None = None,
    time_context: dict | None = None,
):
    """Shorthand: stub LLM that emits `plan(origin=..., goal=...)`.

    `time_context` is optional; when supplied, it rides inside the
    function-call args exactly as the real Gemini output would, so the
    orchestrator's _resolve_time_context path is exercised.
    """
    args: dict = {"origin": origin, "goal": goal}
    if time_context is not None:
        args["time_context"] = time_context
    return StubLLM(("plan", args), answer_text)


def build_graph_and_weights(edges):
    """Turn a list of (a, b, t) edges into (graph_dict, weights_dict)."""
    graph: dict[str, list[tuple[str, int]]] = {}
    weights: dict[tuple[str, str], int] = {}
    for a, b, t in edges:
        graph.setdefault(a, []).append((b, t))
        weights[(a, b)] = t
    return graph, weights
