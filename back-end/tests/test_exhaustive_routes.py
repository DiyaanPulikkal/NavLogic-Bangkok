from tests.helpers import OrchestratorNoLLM, build_graph_and_weights


def test_exhaustive_find_route_all_pairs():
    orchestrator = OrchestratorNoLLM()
    edges = orchestrator.prolog.get_all_edges()
    graph, weights = build_graph_and_weights(edges)

    stations = sorted(orchestrator.prolog.get_all_station_names())

    for start in stations:
        for end in stations:
            if start == end:
                continue
            path, cost = orchestrator._dijkstra(graph, start, end)
            assert path is not None, f"No path found from {start} to {end}"
            assert path[0] == start
            assert path[-1] == end
            assert len(path) == len(set(path)), f"Cycle detected in path: {path}"

            computed_cost = 0
            for a, b in zip(path, path[1:]):
                assert (a, b) in weights, f"Missing edge: {a} -> {b}"
                computed_cost += weights[(a, b)]

            assert computed_cost == cost
            assert cost >= 0, f"Negative cost detected: {cost}"

def test_route_symmetry():
    orchestrator = OrchestratorNoLLM()
    edges = orchestrator.prolog.get_all_edges()
    graph, weights = build_graph_and_weights(edges)

    stations = sorted(orchestrator.prolog.get_all_station_names())

    for start in stations:
        for end in stations:
            if start == end:
                continue

            path1, cost1 = orchestrator._dijkstra(graph, start, end)
            path2, cost2 = orchestrator._dijkstra(graph, end, start)

            assert cost1 == cost2, f"Asymmetric cost: {start}->{end} vs {end}->{start}"