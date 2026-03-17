import json
from typing import Optional

from app.models import Context, Persona
from app.schemas import ContextResponse, PersonaOwnerResponse, PersonaPublicResponse


def serialize_persona_data(data: Optional[dict]) -> Optional[str]:
    """Convert dict to JSON string for storage"""
    if data is None:
        return None
    return json.dumps(data)


def deserialize_persona_data(data: Optional[str]) -> Optional[dict]:
    """Convert JSON string from storage to dict"""
    if data is None:
        return None
    return json.loads(data)


def context_to_response(context: Context | None) -> ContextResponse | None:
    """Convert Context model to response"""
    if context is None:
        return None
    return ContextResponse(id=context.id, name=context.name, description=context.description)


def persona_to_public_response(persona: Persona) -> PersonaPublicResponse:
    """Convert Persona model to public response (no access_token)"""
    return PersonaPublicResponse(
        id=persona.id,
        user_id=persona.user_id,
        name=persona.name,
        is_public=persona.is_public,
        context=context_to_response(persona.context),
        data=deserialize_persona_data(persona.data),
        created_at=persona.created_at,
        updated_at=persona.updated_at,
    )


def persona_to_owner_response(persona: Persona) -> PersonaOwnerResponse:
    """Convert Persona model to owner response (includes access_token)"""
    return PersonaOwnerResponse(
        id=persona.id,
        user_id=persona.user_id,
        name=persona.name,
        is_public=persona.is_public,
        context=context_to_response(persona.context),
        data=deserialize_persona_data(persona.data),
        access_token=persona.access_token,
        created_at=persona.created_at,
        updated_at=persona.updated_at,
    )
