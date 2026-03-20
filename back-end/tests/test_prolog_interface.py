from engine.prolog import PrologInterface


def test_is_valid_query():
    interface = PrologInterface()
    assert interface.is_valid_query("line_of('Siam (CEN)', Line).")
    assert not interface.is_valid_query("invalid")


def test_query_success_and_invalid():
    interface = PrologInterface()
    result = interface.query("line_of('Siam (CEN)', Line).")
    assert result

    assert interface.query("invalid") is None


def test_query_exception_path():
    interface = PrologInterface()

    def boom(_):
        raise RuntimeError("boom")

    interface.prolog.query = boom
    result = interface.query("line_of('Siam (CEN)', Line).")
    assert "Error executing query" in result


def test_prolog_helpers():
    interface = PrologInterface()

    edges = interface.get_all_edges()
    assert edges

    station_lines = interface.get_station_lines()
    assert "Siam (CEN)" in station_lines
    assert len(station_lines["Siam (CEN)"]) >= 2

    assert interface.resolve_location("Grand Palace") == "Sanam Chai (BL31)"
    assert interface.resolve_location("Narnia") is None

    assert interface.is_valid_station("Siam (CEN)")
    assert not interface.is_valid_station("Narnia")

    stations = interface.get_all_station_names()
    assert "Siam (CEN)" in stations

def test_query_empty_string():
    interface = PrologInterface()
    assert interface.query("") is None

def test_query_malformed_but_structured():
    interface = PrologInterface()
    # Looks like Prolog but invalid syntax
    result = interface.query("line_of(Siam, Line)")
    assert result is None or "Error" in str(result)

def test_station_names_match_station_lines():
    interface = PrologInterface()

    stations = set(interface.get_all_station_names())
    station_lines = set(interface.get_station_lines().keys())

    assert stations == station_lines

def test_query_no_results():
    interface = PrologInterface()
    result = interface.query("line_of('Nonexistent Station', Line).")
    
    assert result == [] or result is None