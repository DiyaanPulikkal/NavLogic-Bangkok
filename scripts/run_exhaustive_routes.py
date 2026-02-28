import time

from Orchestrator import Orchestrator
from prolog import PrologInterface


class OrchestratorNoLLM(Orchestrator):
    def __init__(self):
        self.llm = None
        self.prolog = PrologInterface()
        self._station_lines_cache = None
        self._all_stations_cache = None


def build_graph_and_weights(edges):
    graph = {}
    weights = {}
    for a, b, t in edges:
        graph.setdefault(a, []).append((b, t))
        weights[(a, b)] = t
    return graph, weights


def main():
    orchestrator = OrchestratorNoLLM()
    edges = orchestrator.prolog.get_all_edges()
    graph, weights = build_graph_and_weights(edges)
    stations = sorted(orchestrator.prolog.get_all_station_names())

    total_pairs = 0
    failures = 0
    start_time = time.time()

    for start in stations:
        for end in stations:
            if start == end:
                continue
            total_pairs += 1
            path, cost = orchestrator._dijkstra(graph, start, end)
            if path is None:
                failures += 1
                continue

            computed_cost = 0
            for a, b in zip(path, path[1:]):
                computed_cost += weights[(a, b)]

            if computed_cost != cost:
                failures += 1

    elapsed = time.time() - start_time
    print(f"Checked {total_pairs} ordered station pairs in {elapsed:.2f}s")
    print(f"Failures: {failures}")


if __name__ == "__main__":
    main()

