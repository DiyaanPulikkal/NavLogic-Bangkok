import re

from tests.helpers import OrchestratorNoLLM, make_orchestrator_with_llm_result


def test_handle_no_llm_result():
    orchestrator = make_orchestrator_with_llm_result(None)
    result, history = orchestrator.handle("hi")
    assert result["type"] == "error"
    assert "couldn't process" in result["data"]["message"]


def test_handle_unknown_function():
    orchestrator = make_orchestrator_with_llm_result(("mystery", {}))
    result, history = orchestrator.handle("hi")
    assert result["type"] == "error"
    assert "Unknown function" in result["data"]["message"]


def test_handle_line_of():
    orchestrator = make_orchestrator_with_llm_result(("line_of", {"station_name": "Mo Chit"}))
    result, history = orchestrator.handle("line")
    assert result["type"] == "answer"
    assert "bts_sukhumvit" in result["data"]["answer"]


def test_handle_same_line():
    orchestrator = make_orchestrator_with_llm_result(
        ("same_line", {"station_a": "On Nut", "station_b": "Bearing"})
    )
    result, history = orchestrator.handle("same")
    assert result["type"] == "answer"
    assert result["data"]["answer"] == "Yes."


def test_handle_is_transfer_station():
    orchestrator = make_orchestrator_with_llm_result(
        ("is_transfer_station", {"station_name": "Siam"})
    )
    result, history = orchestrator.handle("transfer")
    assert result["type"] == "answer"
    assert result["data"]["answer"] == "Yes."


def test_handle_needs_transfer():
    orchestrator = make_orchestrator_with_llm_result(
        ("needs_transfer", {"station_a": "Asok", "station_b": "Silom"})
    )
    result, history = orchestrator.handle("transfer")
    assert result["type"] == "answer"
    assert result["data"]["answer"] == "Yes."


def test_handle_attraction_near_station():
    orchestrator = make_orchestrator_with_llm_result(
        ("attraction_near_station", {"attraction_name": "Grand Palace"})
    )
    result, history = orchestrator.handle("attraction")
    assert result["type"] == "answer"
    assert "Sanam Chai (BL31)" in result["data"]["answer"]


def test_handle_find_route_invalid_location():
    orchestrator = make_orchestrator_with_llm_result(
        ("find_route", {"start": "Narnia", "end": "Siam"})
    )
    result, history = orchestrator.handle("route")
    assert result["type"] == "error"
    assert result["data"]["message"] == "Unknown location: 'Narnia'."


def test_handle_find_route_valid():
    orchestrator = make_orchestrator_with_llm_result(
        ("find_route", {"start": "Siam", "end": "Asok"})
    )
    result, history = orchestrator.handle("route")
    assert result["type"] == "route"
    assert result["data"]["from"] == "Siam (CEN)"
    assert result["data"]["to"] == "Asok (E4)"
    assert result["data"]["total_time"] > 0
    assert len(result["data"]["steps"]) > 0


def test_handle_text_response():
    orchestrator = make_orchestrator_with_llm_result("Hello! How can I help you?")
    result, history = orchestrator.handle("hello")
    assert result["type"] == "answer"
    assert result["data"]["answer"] == "Hello! How can I help you?"


def test_resolve_location_cases():
    orchestrator = OrchestratorNoLLM()

    assert orchestrator._resolve_location("Grand Palace") == "Sanam Chai (BL31)"
    assert orchestrator._resolve_location("Siam (CEN)") == "Siam (CEN)"
    assert orchestrator._resolve_location("Asok") == "Asok (E4)"
    assert orchestrator._resolve_location("Chit") == "Chit Lom (E1)"
    assert orchestrator._resolve_location("Narnia") is None

    # Typo tolerance via edit-distance fallback
    assert orchestrator._resolve_location("Saim") == "Siam (CEN)"


def test_prolog_station_lines_and_fuzzy_match():
    orchestrator = OrchestratorNoLLM()

    # Station lines are fetched from Prolog
    station_lines = orchestrator.prolog.get_station_lines()
    assert isinstance(station_lines, dict)
    assert len(station_lines) > 0

    # Fuzzy matching is now delegated to Prolog
    matches = orchestrator.prolog.fuzzy_match_station("Siam")
    assert any("Siam" in m for m in matches)


def test_find_and_format_route_no_path():
    orchestrator = OrchestratorNoLLM()
    result = orchestrator._find_and_format_route("Unknown Station", "Siam (CEN)")
    assert result["type"] == "error"
    assert "No route found" in result["data"]["message"]


def test_build_route_steps_with_transfer():
    orchestrator = OrchestratorNoLLM()

    path = ["Asok (E4)", "Sukhumvit (BL22)", "Silom (BL26)"]
    steps = orchestrator.prolog.build_route_steps(path)
    assert any(s["type"] == "transfer" for s in steps)
    assert any(s["type"] == "ride" for s in steps)


def test_format_route_text():
    orchestrator = OrchestratorNoLLM()
    data = {
        "from": "Siam (CEN)",
        "to": "Asok (E4)",
        "total_time": 6,
        "steps": [
            {
                "type": "ride",
                "line": "BTS Sukhumvit Line",
                "board": "Siam (CEN)",
                "alight": "Asok (E4)",
                "stations": ["Siam (CEN)", "Chit Lom (E1)", "Phloen Chit (E2)", "Nana (E3)", "Asok (E4)"],
            }
        ],
    }
    text = orchestrator._format_route_text(data)
    assert "Route: Siam (CEN)" in text
    assert "Board at : Siam (CEN)" in text
    assert "Alight at: Asok (E4)" in text


def test_format_route_text_with_transfer():
    orchestrator = OrchestratorNoLLM()
    data = {
        "from": "Asok (E4)",
        "to": "Silom (BL26)",
        "total_time": 15,
        "steps": [
            {"type": "transfer", "from": "Asok (E4)", "to": "Sukhumvit (BL22)"},
            {"type": "ride", "line": "MRT Blue Line", "board": "Sukhumvit (BL22)", "alight": "Silom (BL26)", "stations": []},
        ],
    }
    text = orchestrator._format_route_text(data)
    assert "[Transfer] Walk from Asok (E4)" in text
    assert "MRT Blue Line" in text


def test_format_prolog_result_variants():
    orchestrator = OrchestratorNoLLM()

    assert orchestrator._format_prolog_result("Error") == "Error"
    assert orchestrator._format_prolog_result(None) == "No results found."
    assert orchestrator._format_prolog_result([]) == "No."
    assert orchestrator._format_prolog_result([{}]) == "Yes."

    result = orchestrator._format_prolog_result([{"Line": "bts_sukhumvit"}])
    assert re.search(r"Line\s*=\s*bts_sukhumvit", result)

    assert orchestrator._format_prolog_result([{}, {}]) == "Yes."


def test_handle_find_route_invalid_end():
    orchestrator = make_orchestrator_with_llm_result(
        ("find_route", {"start": "Siam", "end": "Narnia"})
    )
    result, history = orchestrator.handle("route")
    assert result["type"] == "error"
    assert result["data"]["message"] == "Unknown location: 'Narnia'."


def test_handle_knowledge_query_unknown_station():
    orchestrator = make_orchestrator_with_llm_result(
        ("line_of", {"station_name": "Narnia"})
    )
    result, history = orchestrator.handle("line")
    assert result["type"] == "error"
    assert result["data"]["message"] == "Unknown location: 'Narnia'."


def test_build_route_steps_line_change():
    orchestrator = OrchestratorNoLLM()

    # Use real stations: BTS Sukhumvit → transfer → MRT Blue
    path = [
        "Siam (CEN)", "Chit Lom (E1)", "Phloen Chit (E2)", "Nana (E3)", "Asok (E4)",
        "Sukhumvit (BL22)", "Silom (BL26)",
    ]
    steps = orchestrator.prolog.build_route_steps(path)
    lines_used = [s["line"] for s in steps if s["type"] == "ride"]
    assert len(lines_used) == 2


def test_orchestrator_real_init(monkeypatch):
    from unittest.mock import MagicMock
    import engine.orchestrator as orch_module
    monkeypatch.setattr(orch_module, "LLMInterface", MagicMock)
    orch = orch_module.Orchestrator()
    assert orch.llm is not None
    assert orch.prolog is not None


def test_handle_text_legacy():
    orchestrator = make_orchestrator_with_llm_result(None)
    text = orchestrator.handle_text("hi")
    assert text == "Sorry, I couldn't process your request."


def test_handle_text_route():
    orchestrator = make_orchestrator_with_llm_result(
        ("find_route", {"start": "Siam", "end": "Asok"})
    )
    text = orchestrator.handle_text("route")
    assert text.startswith("Route: ")
    assert "Siam (CEN)" in text
    assert "Asok (E4)" in text


def test_handle_text_answer():
    orchestrator = make_orchestrator_with_llm_result(
        ("same_line", {"station_a": "On Nut", "station_b": "Bearing"})
    )
    text = orchestrator.handle_text("same")
    assert text == "Yes."


def test_find_route_direct():
    orchestrator = OrchestratorNoLLM()
    result = orchestrator.find_route("Siam", "Asok")
    assert result["type"] == "route"
    assert result["data"]["from"] == "Siam (CEN)"


def test_get_all_stations_with_lines():
    orchestrator = OrchestratorNoLLM()
    stations = orchestrator.get_all_stations_with_lines()
    assert len(stations) > 0
    assert all("name" in s and "lines" in s for s in stations)


def test_get_all_attractions():
    orchestrator = OrchestratorNoLLM()
    attractions = orchestrator.get_all_attractions()
    assert len(attractions) > 0
    assert all("name" in a and "station" in a for a in attractions)


def test_handle_with_history():
    """Verify that handle accepts and passes through history."""
    orchestrator = make_orchestrator_with_llm_result(
        ("find_route", {"start": "Siam", "end": "Asok"})
    )
    fake_history = [{"role": "user", "content": "previous message"}]
    result, returned_history = orchestrator.handle("route", history=fake_history)
    assert result["type"] == "route"
    assert isinstance(returned_history, list)
