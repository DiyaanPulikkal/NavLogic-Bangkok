"""TS-01: User Registration — 4 test cases."""

import uuid
from conftest import BASE_URL, BROWSER_TIMEOUT, register_via_api


class TestUserRegistration:
    """Validates the user registration workflow (FR-1.1)."""

    def test_tc01_01_successful_registration(self, page):
        """TC-01-01: Register with valid data → redirect to home, tokens stored."""
        email = f"newuser_{uuid.uuid4().hex[:8]}@example.com"
        page.goto(f"{BASE_URL}/register")
        page.fill('input[placeholder="Email"]', email)
        page.fill('input[placeholder="Password"]', "SecurePass1")
        page.fill('input[placeholder="Confirm password"]', "SecurePass1")
        page.click('button:has-text("Create Account")')

        # Should redirect to home page
        page.wait_for_url(f"{BASE_URL}/", timeout=BROWSER_TIMEOUT)

        # Verify JWT tokens are stored in localStorage
        access = page.evaluate("localStorage.getItem('access_token')")
        refresh = page.evaluate("localStorage.getItem('refresh_token')")
        assert access is not None, "access_token should be stored"
        assert refresh is not None, "refresh_token should be stored"

    def test_tc01_02_invalid_email_format(self, page):
        """TC-01-02: Invalid email → HTML5 validation blocks submission."""
        page.goto(f"{BASE_URL}/register")
        page.fill('input[placeholder="Email"]', "invalid-email")
        page.fill('input[placeholder="Password"]', "SecurePass1")
        page.fill('input[placeholder="Confirm password"]', "SecurePass1")
        page.click('button:has-text("Create Account")')

        # HTML5 type="email" validation prevents submission — stays on register page
        assert "/register" in page.url

    def test_tc01_03_empty_password(self, page):
        """TC-01-03: Empty password → form not submitted."""
        page.goto(f"{BASE_URL}/register")
        page.fill('input[placeholder="Email"]', "test@example.com")
        # Leave password fields empty and click submit
        page.click('button:has-text("Create Account")')

        # Should stay on register page
        assert "/register" in page.url

    def test_tc01_04_duplicate_email(self, page, api_client):
        """TC-01-04: Already registered email → error message displayed."""
        email = f"existing_{uuid.uuid4().hex[:8]}@example.com"
        register_via_api(api_client, email, "SecurePass1")

        page.goto(f"{BASE_URL}/register")
        page.fill('input[placeholder="Email"]', email)
        page.fill('input[placeholder="Password"]', "SecurePass1")
        page.fill('input[placeholder="Confirm password"]', "SecurePass1")
        page.click('button:has-text("Create Account")')

        # Should display error
        error_el = page.locator("p.text-red-400")
        error_el.wait_for(state="visible", timeout=BROWSER_TIMEOUT)
        assert "Email already registered" in error_el.text_content()
