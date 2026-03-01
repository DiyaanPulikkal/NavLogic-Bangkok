from datetime import datetime, timezone

from sqlalchemy.orm import Session

from db.models import User, Conversation, Message


# ── Users ──

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, email: str, hashed_pw: str) -> User:
    user = User(email=email, hashed_pw=hashed_pw)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ── Conversations ──

def create_conversation(db: Session, user_id: int, title: str = "New conversation") -> Conversation:
    conv = Conversation(user_id=user_id, title=title)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


def get_conversations_for_user(db: Session, user_id: int) -> list[Conversation]:
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )


def get_conversation(db: Session, conversation_id: int, user_id: int) -> Conversation | None:
    return (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == user_id)
        .first()
    )


def update_conversation_title(db: Session, conversation_id: int, user_id: int, title: str) -> Conversation | None:
    conv = get_conversation(db, conversation_id, user_id)
    if conv is None:
        return None
    conv.title = title
    db.commit()
    db.refresh(conv)
    return conv


def delete_conversation(db: Session, conversation_id: int, user_id: int) -> bool:
    conv = get_conversation(db, conversation_id, user_id)
    if conv is None:
        return False
    db.delete(conv)
    db.commit()
    return True


def touch_conversation(db: Session, conversation_id: int):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conv:
        conv.updated_at = datetime.now(timezone.utc)
        db.commit()


# ── Messages ──

def add_message(db: Session, conversation_id: int, role: str, content: str) -> Message:
    msg = Message(conversation_id=conversation_id, role=role, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_messages_for_conversation(db: Session, conversation_id: int) -> list[Message]:
    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )
