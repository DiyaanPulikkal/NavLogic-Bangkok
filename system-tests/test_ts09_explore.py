"""TS-09: Explore Stations and Attractions — 6 test cases."""

from conftest import BASE_URL, BROWSER_TIMEOUT


class TestExplorePage:
    """Validates the Explore page for browsing stations and attractions (FR-4.1)."""

    def test_tc09_01_browse_stations_tab(self, page):
        """TC-09-01: Navigate to /explore → Stations tab active, stations listed."""
        page.goto(f"{BASE_URL}/explore")

        # Stations tab should be active (has orange background)
        stations_tab = page.locator('button:text("Stations")')
        stations_tab.wait_for(state="visible", timeout=BROWSER_TIMEOUT)

        # Station cards should be displayed
        station_cards = page.locator('[class*="grid"] [class*="rounded-xl"][class*="border"]')
        station_cards.first.wait_for(state="visible", timeout=BROWSER_TIMEOUT)
        assert station_cards.count() > 0, "Should display station cards"

    def test_tc09_02_filter_stations_by_line(self, page):
        """TC-09-02: Click a line filter → filtered station results."""
        page.goto(f"{BASE_URL}/explore")

        # Wait for stations to load
        page.locator('[class*="grid"] [class*="rounded-xl"][class*="border"]').first.wait_for(
            state="visible", timeout=BROWSER_TIMEOUT
        )

        # Get initial count
        initial_count = page.locator('[class*="grid"] [class*="rounded-xl"][class*="border"]').count()

        # Click a line filter button (skip the "All" button, click the first line)
        line_buttons = page.locator('div.flex.gap-1\\.5 button')
        # The first button is "All", click the second one (first specific line)
        if line_buttons.count() > 1:
            line_buttons.nth(1).click()
            page.wait_for_timeout(500)

            filtered_count = page.locator('[class*="grid"] [class*="rounded-xl"][class*="border"]').count()
            assert filtered_count < initial_count, "Filtering should reduce the number of stations"
            assert filtered_count > 0, "Filtering should still show some stations"

    def test_tc09_03_search_stations_by_name(self, page):
        """TC-09-03: Search 'Siam' → filtered results contain 'Siam'."""
        page.goto(f"{BASE_URL}/explore")

        # Wait for stations to load
        page.locator('[class*="grid"] [class*="rounded-xl"][class*="border"]').first.wait_for(
            state="visible", timeout=BROWSER_TIMEOUT
        )

        search_input = page.locator('input[placeholder="Search stations..."]')
        search_input.fill("Siam")
        page.wait_for_timeout(500)

        # All visible station cards should contain "Siam"
        station_names = page.locator('[class*="grid"] [class*="rounded-xl"][class*="border"] p.font-medium')
        count = station_names.count()
        assert count > 0, "Should find at least one station matching 'Siam'"
        for i in range(count):
            name = station_names.nth(i).text_content()
            assert "Siam" in name, f"Station '{name}' should contain 'Siam'"

    def test_tc09_04_browse_attractions_tab(self, page):
        """TC-09-04: Click Attractions tab → attractions listed."""
        page.goto(f"{BASE_URL}/explore")

        # Click Attractions tab
        page.click('button:has-text("Attractions")')
        page.wait_for_timeout(500)

        # Attraction cards should be displayed with "Near ..." text
        attraction_cards = page.locator('[class*="grid"] [class*="rounded-xl"][class*="border"]')
        attraction_cards.first.wait_for(state="visible", timeout=BROWSER_TIMEOUT)
        assert attraction_cards.count() > 0, "Should display attraction cards"

        # Verify attraction cards show "Near <station>" text
        near_text = page.locator('text=/Near /')
        assert near_text.count() > 0, "Attraction cards should show 'Near <station>'"

    def test_tc09_05_station_data_displayed_correctly(self, page):
        """TC-09-05: Station cards display name and line badges."""
        page.goto(f"{BASE_URL}/explore")

        # Wait for stations to load
        page.locator('[class*="grid"] [class*="rounded-xl"][class*="border"]').first.wait_for(
            state="visible", timeout=BROWSER_TIMEOUT
        )

        # Verify station cards have both a name and at least one line badge
        first_card = page.locator('[class*="grid"] [class*="rounded-xl"][class*="border"]').first
        station_name = first_card.locator("p.font-medium").text_content()
        assert len(station_name) > 0, "Station card should display a name"

        # Line badges should be present (they use colored backgrounds)
        line_badges = first_card.locator("div.flex.gap-1 span, div.flex.gap-1 div")
        assert line_badges.count() > 0, "Station card should display line badge(s)"

    def test_tc09_06_search_attractions_by_name(self, page):
        """TC-09-06: Search 'Grand Palace' on Attractions tab → filtered results."""
        page.goto(f"{BASE_URL}/explore")

        # Switch to Attractions tab
        page.click('button:has-text("Attractions")')
        page.wait_for_timeout(500)

        search_input = page.locator('input[placeholder="Search attractions..."]')
        search_input.fill("Grand Palace")
        page.wait_for_timeout(500)

        # Should find Grand Palace in results
        attraction_names = page.locator('[class*="grid"] [class*="rounded-xl"][class*="border"] p.font-medium')
        count = attraction_names.count()
        assert count > 0, "Should find at least one attraction matching 'Grand Palace'"
        found = any("Grand Palace" in attraction_names.nth(i).text_content() for i in range(count))
        assert found, "Should find 'Grand Palace' in results"
