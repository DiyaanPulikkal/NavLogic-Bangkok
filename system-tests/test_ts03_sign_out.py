"""TS-03: User Sign Out — 2 test cases."""

from conftest import BASE_URL, BROWSER_TIMEOUT, open_sidebar_if_closed


class TestUserSignOut:
    """Validates user sign-out workflow (FR-1.3)."""

    def test_tc03_01_successful_sign_out(self, logged_in_page):
        """TC-03-01: Sign out clears tokens and redirects to login page."""
        page = logged_in_page

        open_sidebar_if_closed(page)
        page.click('button:has-text("Sign out")')

        # Should redirect to login page
        page.wait_for_url(f"**/login", timeout=BROWSER_TIMEOUT)

        # Tokens should be cleared
        access = page.evaluate("localStorage.getItem('access_token')")
        refresh = page.evaluate("localStorage.getItem('refresh_token')")
        assert access is None, "access_token should be cleared"
        assert refresh is None, "refresh_token should be cleared"

    def test_tc03_02_cannot_access_protected_page_after_sign_out(self, logged_in_page):
        """TC-03-02: After sign out, navigating to home redirects to login."""
        page = logged_in_page

        open_sidebar_if_closed(page)
        page.click('button:has-text("Sign out")')
        page.wait_for_url(f"**/login", timeout=BROWSER_TIMEOUT)

        # Try to access protected home page
        page.goto(f"{BASE_URL}/")
        page.wait_for_url(f"**/login", timeout=BROWSER_TIMEOUT)
        assert "/login" in page.url
