"""TS-04: Conversation / Chat History Management — 6 test cases."""

import uuid
import pytest
from conftest import (
    BASE_URL,
    BROWSER_TIMEOUT,
    LLM_TIMEOUT,
    register_via_api,
    create_conversation_via_api,
    set_auth_tokens,
    auth_header,
    open_sidebar_if_closed,
)


class TestConversationManagement:
    """Validates conversation CRUD and history features (FR-2.1, FR-2.2)."""

    @pytest.mark.llm
    def test_tc04_01_access_previous_conversation(self, logged_in_page):
        """TC-04-01: Send a chat query, verify conversation appears in sidebar."""
        page = logged_in_page

        # Send a message via the chat input
        chat_input = page.locator('input[placeholder="Where do you want to go?"]')
        chat_input.fill("How do I get from Siam to Asok?")
        chat_input.press("Enter")

        # Wait for assistant response (LLM call)
        page.locator(".animate-spin").wait_for(state="hidden", timeout=LLM_TIMEOUT)

        # Verify conversation appears in sidebar
        open_sidebar_if_closed(page)
        history = page.locator("text=History")
        history.wait_for(state="visible", timeout=BROWSER_TIMEOUT)

        # At least one conversation should be listed
        conv_items = page.locator('nav button span.truncate')
        assert conv_items.count() > 0, "Conversation should appear in sidebar"

    def test_tc04_02_list_multiple_conversations(self, page, api_client, registered_user):
        """TC-04-02: Create conversations via API, verify sidebar lists them."""
        token = registered_user["access_token"]
        create_conversation_via_api(api_client, token, "First conversation")
        create_conversation_via_api(api_client, token, "Second conversation")

        # Login via UI
        page.goto(f"{BASE_URL}/login")
        page.fill('input[placeholder="Email"]', registered_user["email"])
        page.fill('input[placeholder="Password"]', registered_user["password"])
        page.click('button:has-text("Sign In")')
        page.wait_for_url(f"{BASE_URL}/", timeout=BROWSER_TIMEOUT)

        open_sidebar_if_closed(page)

        # Wait for conversations to load
        page.locator("text=History").wait_for(state="visible", timeout=BROWSER_TIMEOUT)
        conv_items = page.locator('nav button span.truncate')
        assert conv_items.count() >= 2, "Should list at least 2 conversations"

    def test_tc04_03_delete_conversation(self, page, api_client, registered_user):
        """TC-04-03: Delete a conversation via sidebar, verify removal."""
        token = registered_user["access_token"]
        conv = create_conversation_via_api(api_client, token, "To be deleted")
        conv_id = conv["id"]

        # Login via UI
        page.goto(f"{BASE_URL}/login")
        page.fill('input[placeholder="Email"]', registered_user["email"])
        page.fill('input[placeholder="Password"]', registered_user["password"])
        page.click('button:has-text("Sign In")')
        page.wait_for_url(f"{BASE_URL}/", timeout=BROWSER_TIMEOUT)

        open_sidebar_if_closed(page)
        page.locator("text=History").wait_for(state="visible", timeout=BROWSER_TIMEOUT)

        # Hover over the conversation to reveal delete button
        conv_button = page.locator(f'nav button:has(span.truncate:has-text("To be deleted"))').first
        conv_button.hover()

        # Click delete
        delete_icon = conv_button.locator('span[title="Delete"]')
        delete_icon.click()

        # Verify it disappears from sidebar
        page.wait_for_timeout(1000)
        assert page.locator('text="To be deleted"').count() == 0, "Conversation should be removed"

        # Verify via API that it returns 404
        resp = api_client.get(f"/conversations/{conv_id}", headers=auth_header(token))
        assert resp.status_code == 404

    def test_tc04_04_rename_conversation_api(self, api_client, registered_user):
        """TC-04-04: PATCH /conversations/{id} renames the conversation (API-only, no UI)."""
        token = registered_user["access_token"]
        conv = create_conversation_via_api(api_client, token, "Original title")
        conv_id = conv["id"]

        resp = api_client.patch(
            f"/conversations/{conv_id}",
            json={"title": "Renamed title"},
            headers=auth_header(token),
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "Renamed title"

    def test_tc04_05_conversation_user_isolation(self, api_client):
        """TC-04-05: User A's conversation is not visible to User B."""
        # Register User A and create a conversation
        user_a = register_via_api(api_client, f"usera_{uuid.uuid4().hex[:8]}@example.com", "SecurePass1")
        conv = create_conversation_via_api(api_client, user_a["access_token"], "User A's chat")
        conv_id = conv["id"]

        # Register User B
        user_b = register_via_api(api_client, f"userb_{uuid.uuid4().hex[:8]}@example.com", "SecurePass1")

        # User B tries to access User A's conversation
        resp = api_client.get(
            f"/conversations/{conv_id}",
            headers=auth_header(user_b["access_token"]),
        )
        assert resp.status_code == 404

        # User B's conversation list should not include User A's conversation
        resp = api_client.get("/conversations", headers=auth_header(user_b["access_token"]))
        assert resp.status_code == 200
        conv_ids = [c["id"] for c in resp.json()]
        assert conv_id not in conv_ids

    def test_tc04_06_conversations_without_auth(self, api_client):
        """TC-04-06: GET /conversations without auth → 401/403."""
        resp = api_client.get("/conversations")
        assert resp.status_code in (401, 403)
