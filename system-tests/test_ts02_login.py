"""TS-02: User Login — 5 test cases."""

from conftest import BASE_URL, API_URL, BROWSER_TIMEOUT, register_via_api, login_via_api


class TestUserLogin:
    """Validates the user login workflow (FR-1.2)."""

    def test_tc02_01_successful_login(self, page, registered_user):
        """TC-02-01: Login with valid credentials → redirect to home, tokens stored."""
        page.goto(f"{BASE_URL}/login")
        page.fill('input[placeholder="Email"]', registered_user["email"])
        page.fill('input[placeholder="Password"]', registered_user["password"])
        page.click('button:has-text("Sign In")')

        page.wait_for_url(f"{BASE_URL}/", timeout=BROWSER_TIMEOUT)

        access = page.evaluate("localStorage.getItem('access_token')")
        refresh = page.evaluate("localStorage.getItem('refresh_token')")
        assert access is not None
        assert refresh is not None

    def test_tc02_02_invalid_password(self, page, registered_user):
        """TC-02-02: Wrong password → error message displayed."""
        page.goto(f"{BASE_URL}/login")
        page.fill('input[placeholder="Email"]', registered_user["email"])
        page.fill('input[placeholder="Password"]', "WrongPassword")
        page.click('button:has-text("Sign In")')

        error_el = page.locator("p.text-red-400")
        error_el.wait_for(state="visible", timeout=BROWSER_TIMEOUT)
        assert "Invalid credentials" in error_el.text_content()

    def test_tc02_03_nonexistent_email(self, page):
        """TC-02-03: Non-existent email → same generic error."""
        page.goto(f"{BASE_URL}/login")
        page.fill('input[placeholder="Email"]', "nobody@example.com")
        page.fill('input[placeholder="Password"]', "SomePass1")
        page.click('button:has-text("Sign In")')

        error_el = page.locator("p.text-red-400")
        error_el.wait_for(state="visible", timeout=BROWSER_TIMEOUT)
        assert "Invalid credentials" in error_el.text_content()

    def test_tc02_04_token_refresh(self, api_client, registered_user):
        """TC-02-04: POST /auth/refresh with valid refresh_token → new tokens."""
        refresh_token = registered_user["refresh_token"]
        resp = api_client.post("/auth/refresh", json={"refresh_token": refresh_token})
        assert resp.status_code == 200

        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        # New tokens should be valid (non-empty strings)
        assert len(data["access_token"]) > 0
        assert len(data["refresh_token"]) > 0

    def test_tc02_05_protected_route_without_token(self, api_client):
        """TC-02-05: POST /query without Authorization header → 401."""
        resp = api_client.post("/query", json={"message": "hello", "conversation_id": 1})
        assert resp.status_code in (401, 403)
