"""Tests for database CRUD operations."""

from db import crud
from auth.hashing import hash_password


# ── Users ──

def test_create_and_get_user(db_session):
    user = crud.create_user(db_session, "alice@example.com", hash_password("pw"))
    assert user.id is not None
    assert user.email == "alice@example.com"

    found = crud.get_user_by_email(db_session, "alice@example.com")
    assert found is not None
    assert found.id == user.id


def test_get_user_by_email_not_found(db_session):
    assert crud.get_user_by_email(db_session, "nobody@example.com") is None


# ── Conversations ──

def test_create_conversation(db_session):
    user = crud.create_user(db_session, "u@example.com", hash_password("pw"))
    conv = crud.create_conversation(db_session, user.id, "Test Chat")
    assert conv.id is not None
    assert conv.title == "Test Chat"
    assert conv.user_id == user.id


def test_create_conversation_default_title(db_session):
    user = crud.create_user(db_session, "u@example.com", hash_password("pw"))
    conv = crud.create_conversation(db_session, user.id)
    assert conv.title == "New conversation"


def test_get_conversations_for_user(db_session):
    user = crud.create_user(db_session, "u@example.com", hash_password("pw"))
    crud.create_conversation(db_session, user.id, "First")
    crud.create_conversation(db_session, user.id, "Second")

    convs = crud.get_conversations_for_user(db_session, user.id)
    assert len(convs) == 2


def test_get_conversations_for_user_empty(db_session):
    user = crud.create_user(db_session, "u@example.com", hash_password("pw"))
    convs = crud.get_conversations_for_user(db_session, user.id)
    assert convs == []


def test_get_conversation_with_ownership(db_session):
    user_a = crud.create_user(db_session, "a@example.com", hash_password("pw"))
    user_b = crud.create_user(db_session, "b@example.com", hash_password("pw"))
    conv = crud.create_conversation(db_session, user_a.id, "A's chat")

    # Owner can access
    assert crud.get_conversation(db_session, conv.id, user_a.id) is not None
    # Non-owner cannot
    assert crud.get_conversation(db_session, conv.id, user_b.id) is None


def test_update_conversation_title(db_session):
    user = crud.create_user(db_session, "u@example.com", hash_password("pw"))
    conv = crud.create_conversation(db_session, user.id, "Old")

    updated = crud.update_conversation_title(db_session, conv.id, user.id, "New")
    assert updated is not None
    assert updated.title == "New"


def test_update_conversation_title_not_found(db_session):
    user = crud.create_user(db_session, "u@example.com", hash_password("pw"))
    assert crud.update_conversation_title(db_session, 9999, user.id, "X") is None


def test_delete_conversation(db_session):
    user = crud.create_user(db_session, "u@example.com", hash_password("pw"))
    conv = crud.create_conversation(db_session, user.id, "To Delete")

    assert crud.delete_conversation(db_session, conv.id, user.id) is True
    assert crud.get_conversation(db_session, conv.id, user.id) is None


def test_delete_conversation_not_found(db_session):
    user = crud.create_user(db_session, "u@example.com", hash_password("pw"))
    assert crud.delete_conversation(db_session, 9999, user.id) is False


def test_delete_conversation_wrong_user(db_session):
    user_a = crud.create_user(db_session, "a@example.com", hash_password("pw"))
    user_b = crud.create_user(db_session, "b@example.com", hash_password("pw"))
    conv = crud.create_conversation(db_session, user_a.id, "A's chat")

    assert crud.delete_conversation(db_session, conv.id, user_b.id) is False
    # Still exists for user A
    assert crud.get_conversation(db_session, conv.id, user_a.id) is not None


def test_touch_conversation(db_session):
    user = crud.create_user(db_session, "u@example.com", hash_password("pw"))
    conv = crud.create_conversation(db_session, user.id, "Chat")
    original_updated = conv.updated_at

    import time
    time.sleep(0.01)
    crud.touch_conversation(db_session, conv.id)
    db_session.refresh(conv)
    assert conv.updated_at >= original_updated


# ── Messages ──

def test_add_and_get_messages(db_session):
    user = crud.create_user(db_session, "u@example.com", hash_password("pw"))
    conv = crud.create_conversation(db_session, user.id, "Chat")

    msg1 = crud.add_message(db_session, conv.id, "user", "Hello")
    msg2 = crud.add_message(db_session, conv.id, "model", "Hi there!")

    assert msg1.role == "user"
    assert msg2.role == "model"

    messages = crud.get_messages_for_conversation(db_session, conv.id)
    assert len(messages) == 2
    assert messages[0].content == "Hello"
    assert messages[1].content == "Hi there!"


def test_get_messages_empty_conversation(db_session):
    user = crud.create_user(db_session, "u@example.com", hash_password("pw"))
    conv = crud.create_conversation(db_session, user.id, "Empty")
    messages = crud.get_messages_for_conversation(db_session, conv.id)
    assert messages == []


def test_cascade_delete_messages(db_session):
    """Deleting a conversation should cascade-delete its messages."""
    user = crud.create_user(db_session, "u@example.com", hash_password("pw"))
    conv = crud.create_conversation(db_session, user.id, "Chat")
    crud.add_message(db_session, conv.id, "user", "Hello")
    crud.add_message(db_session, conv.id, "model", "Hi")

    crud.delete_conversation(db_session, conv.id, user.id)
    # Messages should be gone
    messages = crud.get_messages_for_conversation(db_session, conv.id)
    assert messages == []
