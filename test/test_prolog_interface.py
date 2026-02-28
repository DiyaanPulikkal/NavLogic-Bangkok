from prolog import PrologInterface


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

