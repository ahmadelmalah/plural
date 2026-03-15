"""
Comprehensive unit tests for Plural - Identity Management API.

Tests cover:
- User CRUD operations
- Persona CRUD operations
- Privacy/access control (public vs private personas)
- Cascade delete behavior
- Validation errors
- Edge cases
"""

import pytest


class TestRoot:
    """Tests for the root endpoint."""

    def test_root_returns_landing_page(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "Plural" in response.text
        assert "One Identity" in response.text


class TestUserCreate:
    """Tests for POST /api/users."""

    def test_create_user_success(self, client):
        response = client.post(
            "/api/users",
            json={"email": "new@example.com", "username": "newuser"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "new@example.com"
        assert data["username"] == "newuser"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_user_duplicate_email(self, client, sample_user):
        response = client.post(
            "/api/users",
            json={"email": "test@example.com", "username": "different"}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Email already registered"

    def test_create_user_duplicate_username(self, client, sample_user):
        response = client.post(
            "/api/users",
            json={"email": "different@example.com", "username": "testuser"}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Username already taken"

    def test_create_user_invalid_email(self, client):
        response = client.post(
            "/api/users",
            json={"email": "not-an-email", "username": "testuser"}
        )
        assert response.status_code == 422  # Validation error

    def test_create_user_missing_email(self, client):
        response = client.post(
            "/api/users",
            json={"username": "testuser"}
        )
        assert response.status_code == 422

    def test_create_user_missing_username(self, client):
        response = client.post(
            "/api/users",
            json={"email": "test@example.com"}
        )
        assert response.status_code == 422

    def test_create_user_username_too_short(self, client):
        response = client.post(
            "/api/users",
            json={"email": "test@example.com", "username": "ab"}
        )
        assert response.status_code == 422


class TestUserList:
    """Tests for GET /api/users."""

    def test_list_users_empty(self, client):
        response = client.get("/api/users")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_users_with_data(self, client):
        # Create multiple users
        client.post("/api/users", json={"email": "user1@example.com", "username": "user1"})
        client.post("/api/users", json={"email": "user2@example.com", "username": "user2"})
        client.post("/api/users", json={"email": "user3@example.com", "username": "user3"})

        response = client.get("/api/users")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3


class TestUserGet:
    """Tests for GET /api/users/{user_id}."""

    def test_get_user_success(self, client, sample_user):
        response = client.get(f"/api/users/{sample_user['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
        assert "personas" in data

    def test_get_user_not_found(self, client):
        response = client.get("/api/users/99999")
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"

    def test_get_user_only_shows_public_personas(self, client, sample_user_with_personas):
        user_id = sample_user_with_personas["user"]["id"]
        response = client.get(f"/api/users/{user_id}")
        assert response.status_code == 200
        data = response.json()

        # Should only have the public persona
        assert len(data["personas"]) == 1
        assert data["personas"][0]["name"] == "Professional"
        assert data["personas"][0]["is_public"] is True


class TestUserUpdate:
    """Tests for PUT /api/users/{user_id}."""

    def test_update_user_email(self, client, sample_user):
        response = client.put(
            f"/api/users/{sample_user['id']}",
            json={"email": "updated@example.com"}
        )
        assert response.status_code == 200
        assert response.json()["email"] == "updated@example.com"

    def test_update_user_username(self, client, sample_user):
        response = client.put(
            f"/api/users/{sample_user['id']}",
            json={"username": "updateduser"}
        )
        assert response.status_code == 200
        assert response.json()["username"] == "updateduser"

    def test_update_user_not_found(self, client):
        response = client.put(
            "/api/users/99999",
            json={"email": "test@example.com"}
        )
        assert response.status_code == 404

    def test_update_user_duplicate_email(self, client, sample_user):
        # Create another user
        client.post("/api/users", json={"email": "other@example.com", "username": "other"})

        # Try to update to that email
        response = client.put(
            f"/api/users/{sample_user['id']}",
            json={"email": "other@example.com"}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Email already registered"

    def test_update_user_duplicate_username(self, client, sample_user):
        # Create another user
        client.post("/api/users", json={"email": "other@example.com", "username": "other"})

        # Try to update to that username
        response = client.put(
            f"/api/users/{sample_user['id']}",
            json={"username": "other"}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Username already taken"


class TestUserDelete:
    """Tests for DELETE /api/users/{user_id}."""

    def test_delete_user_success(self, client, sample_user):
        response = client.delete(f"/api/users/{sample_user['id']}")
        assert response.status_code == 204

        # Verify user is gone
        response = client.get(f"/api/users/{sample_user['id']}")
        assert response.status_code == 404

    def test_delete_user_not_found(self, client):
        response = client.delete("/api/users/99999")
        assert response.status_code == 404


class TestContextList:
    """Tests for GET /api/contexts."""

    def test_list_contexts_empty(self, client):
        response = client.get("/api/contexts")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_contexts_with_data(self, client, sample_contexts):
        response = client.get("/api/contexts")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        # Should be sorted by name
        names = [c["name"] for c in data]
        assert names == sorted(names)

    def test_context_response_fields(self, client, sample_contexts):
        response = client.get("/api/contexts")
        data = response.json()
        context = data[0]
        assert "id" in context
        assert "name" in context
        assert "description" in context


class TestPersonaCreate:
    """Tests for POST /api/users/{user_id}/personas."""

    def test_create_public_persona(self, client, sample_user, sample_contexts):
        response = client.post(
            f"/api/users/{sample_user['id']}/personas",
            json={
                "name": "Gamer",
                "is_public": True,
                "context_id": sample_contexts["Gaming"].id,
                "data": {"steam_id": "12345", "rank": "Diamond"}
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Gamer"
        assert data["is_public"] is True
        assert data["data"]["steam_id"] == "12345"
        assert data["access_token"] is None  # Public personas don't need a token
        assert data["context"]["name"] == "Gaming"

    def test_create_private_persona(self, client, sample_user, sample_contexts):
        response = client.post(
            f"/api/users/{sample_user['id']}/personas",
            json={
                "name": "Legal",
                "is_public": False,
                "context_id": sample_contexts["Legal"].id,
                "data": {"ssn": "123-45-6789"}
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Legal"
        assert data["is_public"] is False
        assert "access_token" in data

    def test_create_persona_user_not_found(self, client, sample_contexts):
        response = client.post(
            "/api/users/99999/personas",
            json={"name": "Test", "is_public": True, "context_id": sample_contexts["Professional"].id}
        )
        assert response.status_code == 404

    def test_create_persona_without_data(self, client, sample_user, sample_contexts):
        response = client.post(
            f"/api/users/{sample_user['id']}/personas",
            json={"name": "Empty", "is_public": True, "context_id": sample_contexts["Professional"].id}
        )
        assert response.status_code == 201
        assert response.json()["data"] is None

    def test_create_persona_name_too_short(self, client, sample_user, sample_contexts):
        response = client.post(
            f"/api/users/{sample_user['id']}/personas",
            json={"name": "", "is_public": True, "context_id": sample_contexts["Professional"].id}
        )
        assert response.status_code == 422

    def test_create_persona_missing_context_id(self, client, sample_user):
        response = client.post(
            f"/api/users/{sample_user['id']}/personas",
            json={"name": "Test", "is_public": True}
        )
        assert response.status_code == 422

    def test_create_persona_invalid_context_id(self, client, sample_user):
        response = client.post(
            f"/api/users/{sample_user['id']}/personas",
            json={"name": "Test", "is_public": True, "context_id": 99999}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Context not found"


class TestPersonaList:
    """Tests for GET /api/users/{user_id}/personas."""

    def test_list_personas_empty(self, client, sample_user):
        response = client.get(f"/api/users/{sample_user['id']}/personas")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_personas_only_public(self, client, sample_user_with_personas):
        user_id = sample_user_with_personas["user"]["id"]
        response = client.get(f"/api/users/{user_id}/personas")
        assert response.status_code == 200
        data = response.json()

        # Should only show public personas
        assert len(data) == 1
        assert data[0]["name"] == "Professional"

    def test_list_personas_filter_by_context(self, client, sample_user_with_personas):
        user_id = sample_user_with_personas["user"]["id"]

        # Filter by Professional context — should return the public persona
        response = client.get(f"/api/users/{user_id}/personas?context=Professional")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Professional"

    def test_list_personas_filter_by_context_case_insensitive(self, client, sample_user_with_personas):
        user_id = sample_user_with_personas["user"]["id"]

        response = client.get(f"/api/users/{user_id}/personas?context=professional")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_list_personas_filter_by_nonexistent_context(self, client, sample_user_with_personas):
        user_id = sample_user_with_personas["user"]["id"]

        response = client.get(f"/api/users/{user_id}/personas?context=Nonexistent")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_personas_user_not_found(self, client):
        response = client.get("/api/users/99999/personas")
        assert response.status_code == 404


class TestPersonaGet:
    """Tests for GET /api/personas/{persona_id}."""

    def test_get_public_persona_without_token(self, client, sample_user_with_personas):
        public_persona = sample_user_with_personas["public_persona"]
        response = client.get(f"/api/personas/{public_persona['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Professional"
        assert "access_token" not in data  # Public response excludes token

    def test_get_private_persona_without_token_forbidden(self, client, sample_user_with_personas):
        private_persona = sample_user_with_personas["private_persona"]
        response = client.get(f"/api/personas/{private_persona['id']}")
        assert response.status_code == 403
        assert response.json()["detail"] == "Access token required for private personas"

    def test_get_private_persona_with_valid_token(self, client, sample_user_with_personas):
        private_persona = sample_user_with_personas["private_persona"]
        response = client.get(
            f"/api/personas/{private_persona['id']}",
            headers={"X-Access-Token": private_persona["access_token"]}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Legal"
        assert data["data"]["full_name"] == "Test User"

    def test_get_private_persona_with_invalid_token(self, client, sample_user_with_personas):
        private_persona = sample_user_with_personas["private_persona"]
        response = client.get(
            f"/api/personas/{private_persona['id']}",
            headers={"X-Access-Token": "invalid-token"}
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Invalid access token"

    def test_get_persona_not_found(self, client):
        response = client.get("/api/personas/99999")
        assert response.status_code == 404


class TestPersonaUpdate:
    """Tests for PUT /api/personas/{persona_id}."""

    def test_update_persona_name(self, client, sample_user_with_personas):
        persona = sample_user_with_personas["private_persona"]
        response = client.put(
            f"/api/personas/{persona['id']}",
            headers={"X-Access-Token": persona["access_token"]},
            json={"name": "Work"}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Work"

    def test_update_persona_visibility(self, client, sample_user_with_personas):
        persona = sample_user_with_personas["private_persona"]
        response = client.put(
            f"/api/personas/{persona['id']}",
            headers={"X-Access-Token": persona["access_token"]},
            json={"is_public": True}
        )
        assert response.status_code == 200
        assert response.json()["is_public"] is True
        assert response.json()["access_token"] is None  # Token cleared when made public

    def test_update_persona_data(self, client, sample_user_with_personas):
        persona = sample_user_with_personas["private_persona"]
        response = client.put(
            f"/api/personas/{persona['id']}",
            headers={"X-Access-Token": persona["access_token"]},
            json={"data": {"new_field": "new_value"}}
        )
        assert response.status_code == 200
        assert response.json()["data"]["new_field"] == "new_value"

    def test_update_persona_without_token(self, client, sample_user_with_personas):
        persona = sample_user_with_personas["private_persona"]
        response = client.put(
            f"/api/personas/{persona['id']}",
            json={"name": "Updated"}
        )
        assert response.status_code == 422  # Missing required header

    def test_update_persona_invalid_token(self, client, sample_user_with_personas):
        persona = sample_user_with_personas["private_persona"]
        response = client.put(
            f"/api/personas/{persona['id']}",
            headers={"X-Access-Token": "wrong-token"},
            json={"name": "Updated"}
        )
        assert response.status_code == 403

    def test_update_persona_not_found(self, client):
        response = client.put(
            "/api/personas/99999",
            headers={"X-Access-Token": "any-token"},
            json={"name": "Updated"}
        )
        assert response.status_code == 404


class TestPersonaDelete:
    """Tests for DELETE /api/personas/{persona_id}."""

    def test_delete_persona_success(self, client, sample_user_with_personas):
        persona = sample_user_with_personas["private_persona"]
        response = client.delete(
            f"/api/personas/{persona['id']}",
            headers={"X-Access-Token": persona["access_token"]}
        )
        assert response.status_code == 204

        # Verify persona is gone
        response = client.get(f"/api/personas/{persona['id']}")
        assert response.status_code == 404

    def test_delete_persona_without_token(self, client, sample_user_with_personas):
        persona = sample_user_with_personas["private_persona"]
        response = client.delete(f"/api/personas/{persona['id']}")
        assert response.status_code == 422

    def test_delete_persona_invalid_token(self, client, sample_user_with_personas):
        persona = sample_user_with_personas["private_persona"]
        response = client.delete(
            f"/api/personas/{persona['id']}",
            headers={"X-Access-Token": "wrong-token"}
        )
        assert response.status_code == 403

    def test_delete_persona_not_found(self, client):
        response = client.delete(
            "/api/personas/99999",
            headers={"X-Access-Token": "any-token"}
        )
        assert response.status_code == 404


class TestRegenerateToken:
    """Tests for POST /api/personas/{persona_id}/regenerate-token."""

    def test_regenerate_token_success(self, client, sample_user_with_personas):
        persona = sample_user_with_personas["private_persona"]
        old_token = persona["access_token"]

        response = client.post(
            f"/api/personas/{persona['id']}/regenerate-token",
            headers={"X-Access-Token": old_token}
        )
        assert response.status_code == 200
        new_token = response.json()["access_token"]
        assert new_token != old_token

        # Old token should no longer work
        response = client.get(
            f"/api/personas/{persona['id']}",
            headers={"X-Access-Token": old_token}
        )
        assert response.status_code == 403

        # New token should work
        response = client.get(
            f"/api/personas/{persona['id']}",
            headers={"X-Access-Token": new_token}
        )
        assert response.status_code == 200

    def test_regenerate_token_invalid_token(self, client, sample_user_with_personas):
        persona = sample_user_with_personas["private_persona"]
        response = client.post(
            f"/api/personas/{persona['id']}/regenerate-token",
            headers={"X-Access-Token": "wrong-token"}
        )
        assert response.status_code == 403

    def test_regenerate_token_not_found(self, client):
        response = client.post(
            "/api/personas/99999/regenerate-token",
            headers={"X-Access-Token": "any-token"}
        )
        assert response.status_code == 404


class TestCascadeDelete:
    """Tests for cascade delete behavior."""

    def test_delete_user_deletes_all_personas(self, client, sample_user_with_personas):
        user_id = sample_user_with_personas["user"]["id"]
        public_persona_id = sample_user_with_personas["public_persona"]["id"]
        private_persona_id = sample_user_with_personas["private_persona"]["id"]

        # Delete user
        response = client.delete(f"/api/users/{user_id}")
        assert response.status_code == 204

        # Both personas should be gone
        response = client.get(f"/api/personas/{public_persona_id}")
        assert response.status_code == 404

        response = client.get(f"/api/personas/{private_persona_id}")
        assert response.status_code == 404


class TestPrivacyBoundaries:
    """Tests for privacy enforcement - the core feature of the project."""

    def test_recruiter_sees_only_professional_persona(self, client, sample_contexts):
        """
        Scenario: A recruiter views a user's profile.
        They should only see professional information, not personal/gaming.
        """
        # Create user
        user = client.post(
            "/api/users",
            json={"email": "multidim@example.com", "username": "multidim"}
        ).json()

        # Create professional persona (public)
        client.post(
            f"/api/users/{user['id']}/personas",
            json={
                "name": "Professional",
                "is_public": True,
                "context_id": sample_contexts["Professional"].id,
                "data": {"linkedin": "linkedin.com/in/test", "skills": ["Python"]}
            }
        )

        # Create gamer persona (public - user chose to share)
        client.post(
            f"/api/users/{user['id']}/personas",
            json={
                "name": "Gamer",
                "is_public": True,
                "context_id": sample_contexts["Gaming"].id,
                "data": {"steam": "steamcommunity.com/id/test"}
            }
        )

        # Create legal persona (private - should never leak)
        legal = client.post(
            f"/api/users/{user['id']}/personas",
            json={
                "name": "Legal",
                "is_public": False,
                "context_id": sample_contexts["Legal"].id,
                "data": {"ssn": "123-45-6789", "real_name": "John Doe"}
            }
        ).json()

        # Get user profile (what a recruiter would see)
        profile = client.get(f"/api/users/{user['id']}").json()

        # Should see Professional and Gamer (both public)
        persona_names = [p["name"] for p in profile["personas"]]
        assert "Professional" in persona_names
        assert "Gamer" in persona_names
        assert "Legal" not in persona_names

        # Direct access to legal persona should fail
        response = client.get(f"/api/personas/{legal['id']}")
        assert response.status_code == 403

    def test_same_user_different_responses(self, client, sample_contexts):
        """
        Scenario: Same user endpoint returns different data based on access context.
        This is the core "contextual identity" feature.
        """
        # Create user with mixed personas
        user = client.post(
            "/api/users",
            json={"email": "context@example.com", "username": "contextuser"}
        ).json()

        # Public persona
        public = client.post(
            f"/api/users/{user['id']}/personas",
            json={"name": "Public", "is_public": True, "context_id": sample_contexts["Professional"].id, "data": {"visible": True}}
        ).json()

        # Private persona
        private = client.post(
            f"/api/users/{user['id']}/personas",
            json={"name": "Private", "is_public": False, "context_id": sample_contexts["Legal"].id, "data": {"secret": "data"}}
        ).json()

        # Anonymous visitor sees only public
        response = client.get(f"/api/users/{user['id']}")
        assert len(response.json()["personas"]) == 1
        assert response.json()["personas"][0]["name"] == "Public"

        # With token, can access private persona directly
        response = client.get(
            f"/api/personas/{private['id']}",
            headers={"X-Access-Token": private["access_token"]}
        )
        assert response.status_code == 200
        assert response.json()["data"]["secret"] == "data"


class TestDataIntegrity:
    """Tests for data integrity requirements from the success criteria."""

    def test_private_persona_returns_403_without_token(self, client, sample_user_with_personas):
        """Success Criteria: Private Personas must return 403 Forbidden when accessed without a token."""
        private_persona = sample_user_with_personas["private_persona"]
        response = client.get(f"/api/personas/{private_persona['id']}")
        assert response.status_code == 403

    def test_api_returns_distinct_attributes_for_different_contexts(self, client, sample_user_with_personas):
        """Success Criteria: The API must return distinct attributes for the same user ID when requested with different headers."""
        user_id = sample_user_with_personas["user"]["id"]
        private_persona = sample_user_with_personas["private_persona"]

        # Without token - only public data
        response1 = client.get(f"/api/users/{user_id}")
        personas_without_token = response1.json()["personas"]

        # The private persona should not be in the list
        private_names = [p["name"] for p in personas_without_token if p["name"] == "Legal"]
        assert len(private_names) == 0

        # With token - can access private persona
        response2 = client.get(
            f"/api/personas/{private_persona['id']}",
            headers={"X-Access-Token": private_persona["access_token"]}
        )
        assert response2.status_code == 200
        assert response2.json()["name"] == "Legal"

    def test_delete_user_cascades_to_personas(self, client, sample_user_with_personas):
        """Success Criteria: Deleting a User must strictly cascade and remove all associated Personas."""
        user_id = sample_user_with_personas["user"]["id"]
        public_id = sample_user_with_personas["public_persona"]["id"]
        private_id = sample_user_with_personas["private_persona"]["id"]

        # Delete user
        client.delete(f"/api/users/{user_id}")

        # Verify both personas are deleted
        assert client.get(f"/api/personas/{public_id}").status_code == 404
        assert client.get(f"/api/personas/{private_id}").status_code == 404
