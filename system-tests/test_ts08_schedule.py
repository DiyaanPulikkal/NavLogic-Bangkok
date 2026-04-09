"""TS-08: Schedule Planning — 7 test cases."""

import pytest
from conftest import BASE_URL, BROWSER_TIMEOUT, LLM_TIMEOUT


class TestSchedulePlanning:
    """Validates time-constrained trip planning (FR-3.4)."""

    def test_tc08_01_plan_trip_valid(self, api_client):
        """TC-08-01: Schedule Mo Chit → Asok, deadline 08:00 → itineraries returned."""
        resp = api_client.get(
            "/schedule",
            params={"origin": "Mo Chit", "destination": "Asok", "deadline": "08:00"},
        )
        assert resp.status_code == 200

        data = resp.json()
        assert data["type"] == "schedule"
        schedule = data["data"]
        assert "itineraries" in schedule
        assert isinstance(schedule["itineraries"], list)
        assert len(schedule["itineraries"]) > 0, "Should return at least one itinerary"

    def test_tc08_02_plan_trip_with_transfer(self, api_client):
        """TC-08-02: Schedule Mo Chit → Silom → multi-leg itinerary with transfer."""
        resp = api_client.get(
            "/schedule",
            params={"origin": "Mo Chit", "destination": "Silom", "deadline": "08:00"},
        )
        assert resp.status_code == 200

        data = resp.json()
        assert data["type"] == "schedule"
        itineraries = data["data"]["itineraries"]
        assert len(itineraries) > 0

        # At least one itinerary should have multiple legs (transfer)
        has_multi_leg = any(len(itin) > 1 for itin in itineraries)
        assert has_multi_leg, "Cross-line route should have multi-leg itineraries"

    def test_tc08_03_plan_trip_default_deadline(self, api_client):
        """TC-08-03: Schedule without deadline → defaults work."""
        resp = api_client.get(
            "/schedule",
            params={"origin": "Mo Chit", "destination": "Siam"},
        )
        assert resp.status_code == 200

        data = resp.json()
        assert data["type"] == "schedule"
        assert "itineraries" in data["data"]

    def test_tc08_04_no_available_itineraries(self, api_client):
        """TC-08-04: Schedule with very early deadline → error (no trips found)."""
        resp = api_client.get(
            "/schedule",
            params={"origin": "Mo Chit", "destination": "Asok", "deadline": "05:00"},
        )
        assert resp.status_code == 200

        data = resp.json()
        # When no itineraries are found, the API returns an error type
        assert data["type"] == "error"
        assert "No scheduled trips" in data["data"]["message"]

    @pytest.mark.llm
    def test_tc08_05_schedule_via_chat(self, logged_in_page):
        """TC-08-05: Chat schedule query → schedule response."""
        page = logged_in_page

        chat_input = page.locator('input[placeholder="Where do you want to go?"]')
        chat_input.fill("I need to get from Siam to Mo Chit before 9am")
        chat_input.press("Enter")

        page.locator(".animate-spin").wait_for(state="visible", timeout=BROWSER_TIMEOUT)
        page.locator(".animate-spin").wait_for(state="hidden", timeout=LLM_TIMEOUT)

        # Verify schedule-related content in response
        assistant_messages = page.locator('[class*="justify-start"] [class*="rounded-2xl"]')
        last_response = assistant_messages.last.text_content()
        assert len(last_response) > 0, "Should have a non-empty response"

    @pytest.mark.llm
    def test_tc08_06_day_plan_via_chat(self, logged_in_page):
        """TC-08-06: Chat day plan with multiple stops → day plan response."""
        page = logged_in_page

        chat_input = page.locator('input[placeholder="Where do you want to go?"]')
        chat_input.fill(
            "Plan my day: I want to go from Siam to Chatuchak by 9am, then to Asok by 12pm"
        )
        chat_input.press("Enter")

        page.locator(".animate-spin").wait_for(state="visible", timeout=BROWSER_TIMEOUT)
        page.locator(".animate-spin").wait_for(state="hidden", timeout=LLM_TIMEOUT)

        assistant_messages = page.locator('[class*="justify-start"] [class*="rounded-2xl"]')
        last_response = assistant_messages.last.text_content()
        assert len(last_response) > 0, "Should have a non-empty day plan response"

    @pytest.mark.llm
    def test_tc08_07_explore_via_chat(self, logged_in_page):
        """TC-08-07: Chat explore query → explore/nightlife response."""
        page = logged_in_page

        chat_input = page.locator('input[placeholder="Where do you want to go?"]')
        chat_input.fill(
            "I'm at Siam and want to explore the city this evening from 6pm to 10pm"
        )
        chat_input.press("Enter")

        page.locator(".animate-spin").wait_for(state="visible", timeout=BROWSER_TIMEOUT)
        page.locator(".animate-spin").wait_for(state="hidden", timeout=LLM_TIMEOUT)

        assistant_messages = page.locator('[class*="justify-start"] [class*="rounded-2xl"]')
        last_response = assistant_messages.last.text_content()
        assert len(last_response) > 0, "Should have a non-empty explore response"
