import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from db.database import Base, get_db
from db import crud
from auth.hashing import hash_password
from auth.jwt import create_access_token


@pytest.fixture
def db_session():
    """Create a fresh in-memory database for each test.

    Uses StaticPool so every connection shares the same in-memory DB.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def auth_client(monkeypatch, db_session):
    """TestClient wired to the in-memory DB with a mocked orchestrator."""
    from tests.helpers import OrchestratorNoLLM
    import app as app_module

    monkeypatch.setattr(app_module, "Orchestrator", OrchestratorNoLLM)

    from app import app

    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user and return (user, plain_password)."""
    password = "testpassword123"
    user = crud.create_user(db_session, "test@example.com", hash_password(password))
    return user, password


@pytest.fixture
def auth_headers(test_user):
    """Return Authorization headers for the test user."""
    user, _ = test_user
    token = create_access_token({"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}
