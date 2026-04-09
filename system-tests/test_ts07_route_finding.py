"""TS-07: Route Finding — 7 test cases."""

import pytest
from conftest import BASE_URL, BROWSER_TIMEOUT, LLM_TIMEOUT


class TestRouteFinding:
    """Validates transit route finding (FR-3.3)."""

    def test_tc07_01_same_line_route(self, api_client):
        """TC-07-01: Route Siam → Ari on single line, valid travel time."""
        resp = api_client.get("/route", params={"start": "Siam", "end": "Ari"})
        assert resp.status_code == 200

        data = resp.json()
        assert data["type"] == "route"
        route = data["data"]
        assert route["total_time"] > 0
        # Should be a single-line route (one ride segment, no transfers)
        ride_segments = [s for s in route["steps"] if s["type"] == "ride"]
        assert len(ride_segments) == 1, "Siam to Ari should be on a single line"

    def test_tc07_02_route_requiring_transfer(self, api_client):
        """TC-07-02: Route Mo Chit → Silom requires transfer at Siam."""
        resp = api_client.get("/route", params={"start": "Mo Chit", "end": "Silom"})
        assert resp.status_code == 200

        data = resp.json()
        assert data["type"] == "route"
        route = data["data"]
        # Should have transfer step(s)
        transfer_steps = [s for s in route["steps"] if s["type"] == "transfer"]
        assert len(transfer_steps) > 0, "Route should include at least one transfer"

    def test_tc07_03_fuzzy_station_name(self, api_client):
        """TC-07-03: Route 'Saim' → Asok resolves via fuzzy matching."""
        resp = api_client.get("/route", params={"start": "Saim", "end": "Asok"})
        assert resp.status_code == 200

        data = resp.json()
        assert data["type"] == "route"
        route = data["data"]
        # 'Saim' should resolve to 'Siam'
        assert "Siam" in route["from"], f"Expected 'Siam' in from field, got: {route['from']}"

    def test_tc07_04_attraction_name_as_origin(self, api_client):
        """TC-07-04: Route 'Grand Palace' → 'Chatuchak Weekend Market' resolves attractions."""
        resp = api_client.get(
            "/route",
            params={"start": "Grand Palace", "end": "Chatuchak Weekend Market"},
        )
        assert resp.status_code == 200

        data = resp.json()
        assert data["type"] == "route"
        route = data["data"]
        assert route["total_time"] > 0
        assert route["steps"] is not None and len(route["steps"]) > 0

    def test_tc07_05_unknown_location(self, api_client):
        """TC-07-05: Route with unknown location → error response."""
        resp = api_client.get(
            "/route",
            params={"start": "Nonexistent Station", "end": "Siam"},
        )
        assert resp.status_code == 200

        data = resp.json()
        assert data["type"] == "error", f"Expected error type, got: {data['type']}"

    def test_tc07_06_route_page_via_url_params(self, page):
        """TC-07-06: Navigate to /route?from=Siam&to=Asok → route displayed."""
        page.goto(f"{BASE_URL}/route?from=Siam&to=Asok")

        # Wait for route to load (loading spinner disappears)
        page.wait_for_timeout(500)

        # Route header should show origin → destination
        header = page.locator("h1")
        header.wait_for(state="visible", timeout=BROWSER_TIMEOUT)
        header_text = header.text_content()
        assert "Siam" in header_text, f"Expected 'Siam' in header: {header_text}"
        assert "Asok" in header_text, f"Expected 'Asok' in header: {header_text}"

        # Should show travel time
        subtitle = page.locator("text=/~\\d+ min/")
        subtitle.wait_for(state="visible", timeout=BROWSER_TIMEOUT)

    @pytest.mark.llm
    def test_tc07_07_route_via_chat(self, logged_in_page):
        """TC-07-07: Chat 'How do I get from Siam to Asok?' → route response."""
        page = logged_in_page

        chat_input = page.locator('input[placeholder="Where do you want to go?"]')
        chat_input.fill("How do I get from Siam to Asok?")
        chat_input.press("Enter")

        page.locator(".animate-spin").wait_for(state="visible", timeout=BROWSER_TIMEOUT)
        page.locator(".animate-spin").wait_for(state="hidden", timeout=LLM_TIMEOUT)

        # Verify route response appears (should show origin → destination or route steps)
        assistant_messages = page.locator('[class*="justify-start"] [class*="rounded-2xl"]')
        last_response = assistant_messages.last.text_content()
        assert "Siam" in last_response or "Asok" in last_response, \
            f"Expected route info in response: {last_response}"
