"""TS-05: Retrieve Nearest Station to Attraction — 3 test cases."""

import pytest
from conftest import BASE_URL, BROWSER_TIMEOUT, LLM_TIMEOUT, open_sidebar_if_closed


class TestNearestStation:
    """Validates nearest-station-to-attraction queries (FR-3.1)."""

    @pytest.mark.llm
    def test_tc05_01_find_nearest_station_via_chat(self, logged_in_page):
        """TC-05-01: Chat 'nearest to Grand Palace?' → response contains 'Sanam Chai'."""
        page = logged_in_page

        chat_input = page.locator('input[placeholder="Where do you want to go?"]')
        chat_input.fill("What station is nearest to Grand Palace?")
        chat_input.press("Enter")

        # Wait for LLM response
        page.locator(".animate-spin").wait_for(state="visible", timeout=BROWSER_TIMEOUT)
        page.locator(".animate-spin").wait_for(state="hidden", timeout=LLM_TIMEOUT)

        # Check assistant response contains Sanam Chai
        assistant_messages = page.locator('[class*="justify-start"] [class*="rounded-2xl"]')
        last_response = assistant_messages.last.text_content()
        assert "Sanam Chai" in last_response, f"Expected 'Sanam Chai' in response, got: {last_response}"

    @pytest.mark.llm
    def test_tc05_02_find_nearest_station_unknown_attraction(self, logged_in_page):
        """TC-05-02: Chat about unknown attraction → not found message."""
        page = logged_in_page

        chat_input = page.locator('input[placeholder="Where do you want to go?"]')
        chat_input.fill("What station is nearest to Nonexistent Place?")
        chat_input.press("Enter")

        page.locator(".animate-spin").wait_for(state="visible", timeout=BROWSER_TIMEOUT)
        page.locator(".animate-spin").wait_for(state="hidden", timeout=LLM_TIMEOUT)

        # Response should indicate attraction not found
        assistant_messages = page.locator('[class*="justify-start"] [class*="rounded-2xl"]')
        last_response = assistant_messages.last.text_content().lower()
        assert any(
            phrase in last_response
            for phrase in ["not found", "couldn't find", "don't have", "no information", "unknown"]
        ), f"Expected 'not found' indication in response, got: {last_response}"

    def test_tc05_03_attractions_api(self, api_client):
        """TC-05-03: GET /attractions → JSON array with name and station fields."""
        resp = api_client.get("/attractions")
        assert resp.status_code == 200

        data = resp.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Should return at least one attraction"

        for item in data:
            assert "name" in item, "Each attraction should have a 'name' field"
            assert "station" in item, "Each attraction should have a 'station' field"
