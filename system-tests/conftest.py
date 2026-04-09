"""Shared fixtures and helpers for Playwright system tests."""

import uuid
import pytest
import httpx

# ---------------------------------------------------------------------------
# Constants – unique per test session to avoid DB collisions
# ---------------------------------------------------------------------------
UNIQUE = uuid.uuid4().hex[:8]
API_URL = "http://localhost:8000/api"
BASE_URL = "http://localhost:5173"

BROWSER_TIMEOUT = 15_000  # ms
LLM_TIMEOUT = 60_000  # ms – LLM calls can be slow


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def register_via_api(client: httpx.Client, email: str, password: str) -> dict:
    """Register a user via the API and return token dict."""
    resp = client.post("/auth/register", json={"email": email, "password": password})
    resp.raise_for_status()
    return resp.json()


def login_via_api(client: httpx.Client, email: str, password: str) -> dict:
    """Login via the API and return token dict."""
    resp = client.post("/auth/login", json={"email": email, "password": password})
    resp.raise_for_status()
    return resp.json()


def create_conversation_via_api(client: httpx.Client, token: str, title: str = "Test conversation") -> dict:
    """Create a conversation and return its dict."""
    resp = client.post(
        "/conversations",
        json={"title": title},
        headers={"Authorization": f"Bearer {token}"},
    )
    resp.raise_for_status()
    return resp.json()


def auth_header(token: str) -> dict:
    """Return an Authorization header dict."""
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Playwright helpers
# ---------------------------------------------------------------------------

def set_auth_tokens(page, access_token: str, refresh_token: str):
    """Inject JWT tokens into browser localStorage."""
    page.evaluate(
        """([a, r]) => {
            localStorage.setItem('access_token', a);
            localStorage.setItem('refresh_token', r);
        }""",
        [access_token, refresh_token],
    )


def open_sidebar_if_closed(page):
    """Ensure the sidebar is visible."""
    toggle = page.locator('button[title="Open sidebar"]')
    if toggle.is_visible():
        toggle.click()
        page.wait_for_timeout(300)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def api_client():
    """Session-scoped httpx client pointed at the back-end."""
    with httpx.Client(base_url=API_URL, timeout=30) as client:
        yield client


@pytest.fixture(scope="session")
def _health_check(api_client):
    """Fail fast if the servers are not running."""
    try:
        r = api_client.get("/stations")
        assert r.status_code == 200, "Back-end not responding"
    except httpx.ConnectError:
        pytest.exit("Back-end is not running at http://localhost:8000", returncode=1)

    try:
        r = httpx.get(BASE_URL, timeout=5)
        assert r.status_code == 200, "Front-end not responding"
    except httpx.ConnectError:
        pytest.exit("Front-end is not running at http://localhost:5173", returncode=1)


@pytest.fixture(autouse=True)
def _require_servers(_health_check):
    """Autouse fixture to ensure servers are checked once per session."""


@pytest.fixture()
def unique_email():
    """Return a unique email for this test."""
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


@pytest.fixture()
def registered_user(api_client):
    """Register a fresh user and return {email, password, access_token, refresh_token}."""
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "SecurePass1"
    tokens = register_via_api(api_client, email, password)
    return {"email": email, "password": password, **tokens}


@pytest.fixture()
def logged_in_page(page, registered_user):
    """A Playwright page that is already logged in via the UI."""
    page.goto(f"{BASE_URL}/login")
    page.fill('input[placeholder="Email"]', registered_user["email"])
    page.fill('input[placeholder="Password"]', registered_user["password"])
    page.click('button:has-text("Sign In")')
    page.wait_for_url(f"{BASE_URL}/", timeout=BROWSER_TIMEOUT)
    return page
