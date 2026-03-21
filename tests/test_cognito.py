"""
Unit tests for Cognito OIDC authentication flow.

Tests cover:
- Cognito login redirect
- Callback with missing/invalid state
- Callback linking existing user by email
- Callback for returning Cognito user
- Callback for new user (redirect to username picker)
- Username completion flow
- Duplicate username rejection
- Complete page without session data
- Logout redirects to Cognito
"""

import json
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from itsdangerous import TimestampSigner
from starlette.middleware.sessions import SessionMiddleware

from app.models import User
from app.routes.auth import hash_password

SECRET_KEY = "plural-secret-key-change-in-production"


def _set_session_cookie(client, data: dict):
    """Create a signed session cookie for Starlette's SessionMiddleware."""
    signer = TimestampSigner(SECRET_KEY)
    cookie_value = signer.sign(json.dumps(data).encode("utf-8")).decode("utf-8")
    # Remove "session=" prefix format — just set the raw value
    import base64
    payload = base64.b64encode(json.dumps(data).encode("utf-8")).decode("utf-8")
    signed = signer.sign(payload).decode("utf-8")
    client.cookies.set("session", signed)


class TestCognitoLogin:
    """Tests for GET /login/cognito."""

    def test_cognito_login_redirects_to_authorize(self, client):
        with patch("app.routes.auth.COGNITO_DOMAIN", "example.auth.us-west-2.amazoncognito.com"), \
             patch("app.routes.auth.COGNITO_CLIENT_ID", "test-client-id"):
            response = client.get("/login/cognito", follow_redirects=False)
            assert response.status_code == 302
            location = response.headers["location"]
            assert "example.auth.us-west-2.amazoncognito.com/oauth2/authorize" in location
            assert "client_id=test-client-id" in location
            assert "response_type=code" in location
            assert "scope=email+openid+phone" in location

    def test_cognito_login_disabled_without_config(self, client):
        with patch("app.routes.auth.COGNITO_DOMAIN", ""), \
             patch("app.routes.auth.COGNITO_CLIENT_ID", ""):
            response = client.get("/login/cognito", follow_redirects=False)
            assert response.status_code == 302
            assert response.headers["location"].endswith("/login")


def _get_state_from_login(client):
    """Initiate cognito login and extract the state parameter from redirect."""
    import urllib.parse
    with patch("app.routes.auth.COGNITO_DOMAIN", "example.auth.amazoncognito.com"), \
         patch("app.routes.auth.COGNITO_CLIENT_ID", "test-client-id"):
        login_resp = client.get("/login/cognito", follow_redirects=False)
        location = login_resp.headers["location"]
        parsed = urllib.parse.urlparse(location)
        params = urllib.parse.parse_qs(parsed.query)
        return params["state"][0]


def _mock_cognito_callback(client, state, cognito_sub="cognito-123", email="cognito@example.com"):
    """Execute the callback with mocked Cognito responses."""
    mock_token_response = httpx.Response(200, json={"id_token": "fake.jwt.token"})
    mock_jwks_response = httpx.Response(200, json={"keys": [{"kty": "RSA", "kid": "test"}]})
    mock_claims = {"sub": cognito_sub, "email": email}

    with patch("app.routes.auth.COGNITO_DOMAIN", "example.auth.amazoncognito.com"), \
         patch("app.routes.auth.COGNITO_CLIENT_ID", "test-client-id"), \
         patch("app.routes.auth.COGNITO_CLIENT_SECRET", "test-secret"), \
         patch("app.routes.auth.COGNITO_REGION", "us-west-2"), \
         patch("app.routes.auth.COGNITO_POOL_ID", "us-west-2_test"), \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_token_response), \
         patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_jwks_response), \
         patch("app.routes.auth.jwt") as mock_jwt:
        mock_jwt.decode.return_value = mock_claims
        return client.get(
            f"/auth/cognito/callback?code=test-code&state={state}",
            follow_redirects=False,
        )


class TestCognitoCallback:
    """Tests for GET /auth/cognito/callback."""

    def test_callback_missing_code_redirects_to_login(self, client):
        response = client.get("/auth/cognito/callback", follow_redirects=False)
        assert response.status_code == 302
        assert response.headers["location"].endswith("/login")

    def test_callback_missing_state_redirects_to_login(self, client):
        response = client.get("/auth/cognito/callback?code=abc", follow_redirects=False)
        assert response.status_code == 302
        assert response.headers["location"].endswith("/login")

    def test_callback_invalid_state_redirects_to_login(self, client):
        # First set a valid state via the login flow
        _get_state_from_login(client)
        # Then use a wrong state
        response = client.get(
            "/auth/cognito/callback?code=abc&state=wrong-state",
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert response.headers["location"].endswith("/login")

    def test_callback_new_user_redirects_to_complete(self, client, db_session):
        state = _get_state_from_login(client)
        response = _mock_cognito_callback(client, state)
        assert response.status_code == 302
        assert "/auth/cognito/complete" in response.headers["location"]

    def test_callback_existing_cognito_user_logs_in(self, client, db_session):
        user = User(email="cognito@example.com", username="cognitouser", cognito_sub="cognito-123")
        db_session.add(user)
        db_session.commit()

        state = _get_state_from_login(client)
        response = _mock_cognito_callback(client, state)
        assert response.status_code == 302
        assert "/dashboard" in response.headers["location"]

    def test_callback_links_existing_email_user(self, client, db_session):
        user = User(
            email="cognito@example.com",
            username="localuser",
            password_hash=hash_password("password123"),
        )
        db_session.add(user)
        db_session.commit()

        state = _get_state_from_login(client)
        response = _mock_cognito_callback(client, state)
        assert response.status_code == 302
        assert "/dashboard" in response.headers["location"]

        # Verify cognito_sub was linked
        db_session.refresh(user)
        assert user.cognito_sub == "cognito-123"

    def test_callback_token_exchange_failure_redirects_to_login(self, client, db_session):
        state = _get_state_from_login(client)

        mock_error_response = httpx.Response(400, json={"error": "invalid_grant"})
        with patch("app.routes.auth.COGNITO_DOMAIN", "example.auth.amazoncognito.com"), \
             patch("app.routes.auth.COGNITO_CLIENT_ID", "test-client-id"), \
             patch("app.routes.auth.COGNITO_CLIENT_SECRET", "test-secret"), \
             patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_error_response):
            response = client.get(
                f"/auth/cognito/callback?code=bad-code&state={state}",
                follow_redirects=False,
            )
        assert response.status_code == 302
        assert response.headers["location"].endswith("/login")


class TestCognitoComplete:
    """Tests for GET/POST /auth/cognito/complete."""

    def test_complete_page_without_session_redirects(self, client):
        response = client.get("/auth/cognito/complete", follow_redirects=False)
        assert response.status_code == 302
        assert response.headers["location"].endswith("/login")

    def test_complete_page_with_session_shows_form(self, client, db_session):
        # Go through the callback flow to set session naturally
        state = _get_state_from_login(client)
        _mock_cognito_callback(client, state, email="test@example.com")

        # Now the session has cognito_sub and cognito_email
        response = client.get("/auth/cognito/complete")
        assert response.status_code == 200
        assert "test@example.com" in response.text

    def test_complete_creates_user(self, client, db_session):
        # Go through callback to set session
        state = _get_state_from_login(client)
        _mock_cognito_callback(client, state, cognito_sub="cognito-456", email="newuser@example.com")

        response = client.post(
            "/auth/cognito/complete",
            data={"username": "newcognitouser"},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "/dashboard" in response.headers["location"]

        # Verify user was created
        user = db_session.query(User).filter(User.email == "newuser@example.com").first()
        assert user is not None
        assert user.username == "newcognitouser"
        assert user.cognito_sub == "cognito-456"
        assert user.password_hash is None

    def test_complete_duplicate_username_shows_error(self, client, db_session):
        # Create existing user
        existing = User(email="existing@example.com", username="taken", password_hash=hash_password("pass"))
        db_session.add(existing)
        db_session.commit()

        # Go through callback to set session
        state = _get_state_from_login(client)
        _mock_cognito_callback(client, state)

        response = client.post(
            "/auth/cognito/complete",
            data={"username": "taken"},
        )
        assert response.status_code == 200
        assert "already taken" in response.text.lower()

    def test_complete_without_session_redirects(self, client):
        response = client.post(
            "/auth/cognito/complete",
            data={"username": "someuser"},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert response.headers["location"].endswith("/login")


class TestCognitoLogout:
    """Tests for logout with Cognito configured."""

    def test_logout_redirects_to_cognito(self, client):
        with patch("app.routes.auth.COGNITO_DOMAIN", "example.auth.amazoncognito.com"), \
             patch("app.routes.auth.COGNITO_CLIENT_ID", "test-client-id"):
            response = client.get("/logout", follow_redirects=False)
            assert response.status_code == 302
            location = response.headers["location"]
            assert "example.auth.amazoncognito.com/logout" in location
            assert "client_id=test-client-id" in location

    def test_logout_without_cognito_redirects_home(self, client):
        with patch("app.routes.auth.COGNITO_DOMAIN", ""), \
             patch("app.routes.auth.COGNITO_CLIENT_ID", ""):
            response = client.get("/logout", follow_redirects=False)
            assert response.status_code == 302
            assert response.headers["location"].endswith("/")
