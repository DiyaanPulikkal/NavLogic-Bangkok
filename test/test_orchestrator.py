import re

from test.helpers import OrchestratorNoLLM, make_orchestrator_with_llm_result


def test_handle_no_llm_result():
    orchestrator = make_orchestrator_with_llm_result(None)
    assert orchestrator.handle("hi") == "Sorry, I couldn't process your request."


def test_handle_unknown_function():
    orchestrator = make_orchestrator_with_llm_result(("mystery", {}))
    assert orchestrator.handle("hi") == "Unknown function: mystery"


def test_handle_line_of():
    orchestrator = make_orchestrator_with_llm_result(("line_of", {"station_name": "Mo Chit"}))
    response = orchestrator.handle("line")
    assert "bts_sukhumvit" in response


def test_handle_same_line():
    orchestrator = make_orchestrator_with_llm_result(
        ("same_line", {"station_a": "On Nut", "station_b": "Bearing"})
    )
    assert orchestrator.handle("same") == "Yes."


def test_handle_is_transfer_station():
    orchestrator = make_orchestrator_with_llm_result(
        ("is_transfer_station", {"station_name": "Siam"})
    )
    assert orchestrator.handle("transfer") == "Yes."


def test_handle_needs_transfer():
    orchestrator = make_orchestrator_with_llm_result(
        ("needs_transfer", {"station_a": "Asok", "station_b": "Silom"})
    )
    assert orchestrator.handle("transfer") == "Yes."


def test_handle_attraction_near_station():
    orchestrator = make_orchestrator_with_llm_result(
        ("attraction_near_station", {"attraction_name": "Grand Palace"})
    )
    response = orchestrator.handle("attraction")
    assert "Sanam Chai (BL31)" in response


def test_handle_find_route_invalid_location():
    orchestrator = make_orchestrator_with_llm_result(
        ("find_route", {"start": "Narnia", "end": "Siam"})
    )
    assert orchestrator.handle("route") == "Unknown location: 'Narnia'."


def test_handle_find_route_valid():
    orchestrator = make_orchestrator_with_llm_result(
        ("find_route", {"start": "Siam", "end": "Asok"})
    )
    response = orchestrator.handle("route")
    assert response.startswith("Route: ")
    assert "Siam (CEN)" in response
    assert "Asok (E4)" in response


def test_resolve_location_cases():
    orchestrator = OrchestratorNoLLM()

    assert orchestrator._resolve_location("Grand Palace") == "Sanam Chai (BL31)"
    assert orchestrator._resolve_location("Siam (CEN)") == "Siam (CEN)"
    assert orchestrator._resolve_location("Asok") == "Asok (E4)"
    assert orchestrator._resolve_location("Chit") == "Chit Lom (E1)"
    assert orchestrator._resolve_location("Bang") is None
    assert orchestrator._resolve_location("Narnia") is None


def test_get_all_stations_and_lines_cache():
    orchestrator = OrchestratorNoLLM()

    stations_first = orchestrator._get_all_stations()
    stations_second = orchestrator._get_all_stations()
    assert stations_first is stations_second

    lines_first = orchestrator._get_station_lines()
    lines_second = orchestrator._get_station_lines()
    assert lines_first is lines_second


def test_find_and_format_route_no_path():
    orchestrator = OrchestratorNoLLM()
    response = orchestrator._find_and_format_route("Unknown Station", "Siam (CEN)")
    assert response == "No route found from 'Unknown Station' to 'Siam (CEN)'."


def test_format_route_with_transfer():
    orchestrator = OrchestratorNoLLM()
    station_lines = orchestrator.prolog.get_station_lines()

    path = ["Asok (E4)", "Sukhumvit (BL22)", "Silom (BL26)"]
    output = orchestrator._format_route(path, 11, station_lines)
    assert "[Transfer] Walk from Asok (E4)" in output
    assert "MRT Blue Line" in output
    assert "Board at : Sukhumvit (BL22)" in output
    assert "Alight at: Silom (BL26)" in output


def test_format_prolog_result_variants():
    orchestrator = OrchestratorNoLLM()

    assert orchestrator._format_prolog_result("Error") == "Error"
    assert orchestrator._format_prolog_result(None) == "No results found."
    assert orchestrator._format_prolog_result([]) == "No."
    assert orchestrator._format_prolog_result([{}]) == "Yes."

    result = orchestrator._format_prolog_result([{"Line": "bts_sukhumvit"}])
    assert re.search(r"Line\s*=\s*bts_sukhumvit", result)

    # Multiple empty bindings should also be "Yes."
    assert orchestrator._format_prolog_result([{}, {}]) == "Yes."


def test_handle_find_route_invalid_end():
    orchestrator = make_orchestrator_with_llm_result(
        ("find_route", {"start": "Siam", "end": "Narnia"})
    )
    assert orchestrator.handle("route") == "Unknown location: 'Narnia'."


def test_handle_knowledge_query_unknown_station():
    orchestrator = make_orchestrator_with_llm_result(
        ("line_of", {"station_name": "Narnia"})
    )
    assert orchestrator.handle("line") == "Unknown location: 'Narnia'."


def test_format_route_line_change_break():
    orchestrator = OrchestratorNoLLM()
    station_lines = {
        "A": ["line1"],
        "B": ["line1"],
        "C": ["line1", "line2"],
        "D": ["line2"],
    }
    path = ["A", "B", "C", "D"]
    output = orchestrator._format_route(path, 10, station_lines)
    assert "line1" in output
    assert "line2" in output


def test_orchestrator_real_init(monkeypatch):
    from unittest.mock import MagicMock
    import Orchestrator as orch_module
    monkeypatch.setattr(orch_module, "LLMInterface", MagicMock)
    orch = orch_module.Orchestrator()
    assert orch.llm is not None
    assert orch.prolog is not None
    assert orch._station_lines_cache is None
    assert orch._all_stations_cache is None

