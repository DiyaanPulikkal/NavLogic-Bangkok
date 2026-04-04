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


# ── match_station_classified ──

def test_match_station_classified_exact():
    interface = PrologInterface()
    results = interface.match_station_classified("Siam (CEN)")
    assert any(r["station"] == "Siam (CEN)" and r["match_type"] == "exact" for r in results)


def test_match_station_classified_prefix():
    interface = PrologInterface()
    results = interface.match_station_classified("Siam")
    stations = [r["station"] for r in results]
    assert "Siam (CEN)" in stations
    assert all(r["match_type"] in ("exact", "prefix", "substring") for r in results)


def test_match_station_classified_substring():
    interface = PrologInterface()
    results = interface.match_station_classified("Chit")
    stations = [r["station"] for r in results]
    assert len(results) >= 2
    assert any("Mo Chit" in s for s in stations)
    assert any("Chit Lom" in s for s in stations)


def test_match_station_classified_no_match():
    interface = PrologInterface()
    results = interface.match_station_classified("Narnia")
    assert results == []


def test_match_station_classified_deduplication():
    interface = PrologInterface()
    results = interface.match_station_classified("Siam")
    siam_entries = [r for r in results if r["station"] == "Siam (CEN)"]
    assert len(siam_entries) <= 1


# ── suggest_transfer_station ──

def test_suggest_transfer_station_same_station():
    interface = PrologInterface()
    results = interface.suggest_transfer_station("bts_sukhumvit", "bts_silom")
    same_station = [r for r in results if r["type"] == "same_station"]
    assert any(r["station"] == "Siam (CEN)" for r in same_station)


def test_suggest_transfer_station_walk():
    interface = PrologInterface()
    results = interface.suggest_transfer_station("bts_sukhumvit", "mrt_blue")
    assert len(results) > 0
    # Walk transfers show up as transfer_pair compounds — check the Asok↔Sukhumvit pair exists
    stations = [r["station"] if "station" in r else "" for r in results]
    assert any("Asok" in s and "Sukhumvit" in s for s in stations)


def test_suggest_transfer_station_same_line():
    interface = PrologInterface()
    results = interface.suggest_transfer_station("bts_sukhumvit", "bts_sukhumvit")
    assert results == []


# ── get_line_display_name ──

def test_get_line_display_name_known():
    interface = PrologInterface()
    assert interface.get_line_display_name("bts_sukhumvit") == "BTS Sukhumvit Line"
    assert interface.get_line_display_name("mrt_blue") == "MRT Blue Line"
    assert interface.get_line_display_name("airport_rail_link") == "Airport Rail Link"


def test_get_line_display_name_unknown():
    interface = PrologInterface()
    assert interface.get_line_display_name("nonexistent_line") == "nonexistent_line"


# ── plan_trip ──

def test_plan_trip_single_line():
    interface = PrologInterface()
    itineraries = interface.plan_trip("Mo Chit (N8)", "Siam (CEN)", 800)
    assert len(itineraries) > 0
    first = itineraries[0]
    assert first[0]["from"] == "Mo Chit (N8)"
    assert first[-1]["to"] == "Siam (CEN)"


def test_plan_trip_mrt_blue():
    interface = PrologInterface()
    itineraries = interface.plan_trip("Chatuchak Park (BL13)", "Hua Lamphong (BL28)", 800)
    assert len(itineraries) > 0
    assert itineraries[0][-1]["to"] == "Hua Lamphong (BL28)"


def test_plan_trip_impossible_deadline():
    interface = PrologInterface()
    itineraries = interface.plan_trip("Mo Chit (N8)", "Siam (CEN)", 600)
    assert itineraries == []


def test_plan_trip_itinerary_structure():
    interface = PrologInterface()
    itineraries = interface.plan_trip("Mo Chit (N8)", "Siam (CEN)", 800)
    assert len(itineraries) > 0
    for leg in itineraries[0]:
        assert set(leg.keys()) == {"from", "to", "line", "depart", "arrive"}
        assert ":" in leg["depart"]
        assert ":" in leg["arrive"]


# ── attractions_near ──

def test_attractions_near_known():
    interface = PrologInterface()
    results = interface.attractions_near("Siam (CEN)")
    assert "Siam Paragon" in results


def test_attractions_near_unknown():
    interface = PrologInterface()
    results = interface.attractions_near("Nonexistent Station")
    assert results == []


# ── get_attractions_by_station ──

def test_get_attractions_by_station():
    interface = PrologInterface()
    by_station = interface.get_attractions_by_station()
    assert isinstance(by_station, dict)
    assert "Siam (CEN)" in by_station
    assert "Siam Paragon" in by_station["Siam (CEN)"]
    assert len(by_station) > 10


# ── get_nightlife_venues ──

def test_get_nightlife_venues():
    interface = PrologInterface()
    venues = interface.get_nightlife_venues()
    assert isinstance(venues, dict)
    assert len(venues) > 0
    for station, venue_list in venues.items():
        for v in venue_list:
            assert "name" in v
            assert "category" in v


def test_get_nightlife_venues_has_expected_stations():
    interface = PrologInterface()
    venues = interface.get_nightlife_venues()
    assert "Thong Lo (E6)" in venues
    categories = [v["category"] for vlist in venues.values() for v in vlist]
    assert "night_market" in categories