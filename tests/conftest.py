"""
Test configuration and fixtures for Plural API tests.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Context, Persona, User
from main import app, get_db

# Use in-memory SQLite for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override."""
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_contexts(db_session):
    """Create sample contexts and return them."""
    contexts = [
        Context(name="Professional", description="Work and career"),
        Context(name="Gaming", description="Gaming profiles"),
        Context(name="Legal", description="Legal identity"),
    ]
    for ctx in contexts:
        db_session.add(ctx)
    db_session.commit()
    for ctx in contexts:
        db_session.refresh(ctx)
    return {ctx.name: ctx for ctx in contexts}


@pytest.fixture
def sample_user(client):
    """Create a sample user and return the response data."""
    response = client.post(
        "/api/users",
        json={"email": "test@example.com", "username": "testuser"}
    )
    return response.json()


@pytest.fixture
def sample_user_with_personas(client, sample_user, sample_contexts):
    """Create a user with both public and private personas."""
    user_id = sample_user["id"]

    # Create public persona
    public_response = client.post(
        f"/api/users/{user_id}/personas",
        json={
            "name": "Professional",
            "is_public": True,
            "context_id": sample_contexts["Professional"].id,
            "data": {"linkedin": "linkedin.com/in/test", "title": "Engineer"}
        }
    )

    # Create private persona
    private_response = client.post(
        f"/api/users/{user_id}/personas",
        json={
            "name": "Legal",
            "is_public": False,
            "context_id": sample_contexts["Legal"].id,
            "data": {"full_name": "Test User", "ssn": "123-45-6789"}
        }
    )

    return {
        "user": sample_user,
        "public_persona": public_response.json(),
        "private_persona": private_response.json(),
        "contexts": sample_contexts,
    }
