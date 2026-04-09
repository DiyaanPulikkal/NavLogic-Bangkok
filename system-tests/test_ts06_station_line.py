"""TS-06: Retrieve Station's Line — 4 test cases."""

import pytest
from conftest import BASE_URL, BROWSER_TIMEOUT, LLM_TIMEOUT


class TestStationLine:
    """Validates station-line queries (FR-3.2)."""

    @pytest.mark.llm
    def test_tc06_01_query_lines_serving_station(self, logged_in_page):
        """TC-06-01: Chat about Siam lines → mentions Sukhumvit and Silom."""
        page = logged_in_page

        chat_input = page.locator('input[placeholder="Where do you want to go?"]')
        chat_input.fill("What lines does Siam station serve?")
        chat_input.press("Enter")

        page.locator(".animate-spin").wait_for(state="visible", timeout=BROWSER_TIMEOUT)
        page.locator(".animate-spin").wait_for(state="hidden", timeout=LLM_TIMEOUT)

        assistant_messages = page.locator('[class*="justify-start"] [class*="rounded-2xl"]')
        last_response = assistant_messages.last.text_content()
        assert "Sukhumvit" in last_response, f"Expected 'Sukhumvit' in response: {last_response}"
        assert "Silom" in last_response, f"Expected 'Silom' in response: {last_response}"

    @pytest.mark.llm
    def test_tc06_02_check_same_line(self, logged_in_page):
        """TC-06-02: Chat 'Are Siam and Ari on the same line?' → confirmation."""
        page = logged_in_page

        chat_input = page.locator('input[placeholder="Where do you want to go?"]')
        chat_input.fill("Are Siam and Ari on the same line?")
        chat_input.press("Enter")

        page.locator(".animate-spin").wait_for(state="visible", timeout=BROWSER_TIMEOUT)
        page.locator(".animate-spin").wait_for(state="hidden", timeout=LLM_TIMEOUT)

        assistant_messages = page.locator('[class*="justify-start"] [class*="rounded-2xl"]')
        last_response = assistant_messages.last.text_content().lower()
        assert any(
            word in last_response for word in ["yes", "same line", "sukhumvit", "share"]
        ), f"Expected confirmation in response: {last_response}"

    @pytest.mark.llm
    def test_tc06_03_check_transfer_station(self, logged_in_page):
        """TC-06-03: Chat 'Is Siam a transfer station?' → confirmation."""
        page = logged_in_page

        chat_input = page.locator('input[placeholder="Where do you want to go?"]')
        chat_input.fill("Is Siam a transfer station?")
        chat_input.press("Enter")

        page.locator(".animate-spin").wait_for(state="visible", timeout=BROWSER_TIMEOUT)
        page.locator(".animate-spin").wait_for(state="hidden", timeout=LLM_TIMEOUT)

        assistant_messages = page.locator('[class*="justify-start"] [class*="rounded-2xl"]')
        last_response = assistant_messages.last.text_content().lower()
        assert any(
            word in last_response for word in ["yes", "transfer", "interchange", "connect"]
        ), f"Expected transfer confirmation in response: {last_response}"

    def test_tc06_04_stations_api(self, api_client):
        """TC-06-04: GET /stations → JSON array with name and lines fields."""
        resp = api_client.get("/stations")
        assert resp.status_code == 200

        data = resp.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Should return at least one station"

        for item in data:
            assert "name" in item, "Each station should have a 'name' field"
            assert "lines" in item, "Each station should have a 'lines' field"
            assert isinstance(item["lines"], list), "'lines' should be a list"
