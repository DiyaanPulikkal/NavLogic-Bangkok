from engine.orchestrator import Orchestrator
from engine.prolog import PrologInterface


class OrchestratorNoLLM(Orchestrator):
    def __init__(self):
        self.llm = None
        self.prolog = PrologInterface()
        self._station_lines_cache = None
        self._all_stations_cache = None


class StubLLM:
    """Stub that returns a pre-configured result from translate_to_query."""

    def __init__(self, result):
        self._result = result

    def translate_to_query(self, user_input, history=None):
        if history is None:
            history = []
        return self._result, history

    def format_prolog_result(self, function_name, result, history=None):
        if history is None:
            history = []
        return result, history


def make_orchestrator_with_llm_result(result):
    orchestrator = OrchestratorNoLLM()
    orchestrator.llm = StubLLM(result)
    return orchestrator


def build_graph_and_weights(edges):
    graph = {}
    weights = {}
    for a, b, t in edges:
        graph.setdefault(a, []).append((b, t))
        weights[(a, b)] = t
    return graph, weights
