import secrets
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Context, Persona, User
from app.schemas import (
    PersonaCreate,
    PersonaOwnerResponse,
    PersonaPublicResponse,
    PersonaUpdate,
)
from app.utils import (
    persona_to_owner_response,
    persona_to_public_response,
    serialize_persona_data,
)

router = APIRouter()


@router.post(
    "/api/users/{user_id}/personas",
    response_model=PersonaOwnerResponse,
    status_code=status.HTTP_201_CREATED
)
def create_persona(user_id: int, persona_data: PersonaCreate, db: Session = Depends(get_db)):
    """Create a new persona for a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    context = db.query(Context).filter(Context.id == persona_data.context_id).first()
    if not context:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Context not found"
        )

    persona = Persona(
        user_id=user_id,
        name=persona_data.name,
        is_public=persona_data.is_public,
        access_token=None if persona_data.is_public else secrets.token_urlsafe(32),
        context_id=persona_data.context_id,
        data=serialize_persona_data(persona_data.data),
    )
    db.add(persona)
    db.commit()
    db.refresh(persona)
    return persona_to_owner_response(persona)


@router.get("/api/users/{user_id}/personas", response_model=list[PersonaPublicResponse])
def list_user_personas(
    user_id: int,
    context: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all public personas for a user, optionally filtered by context name"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    public_personas = [p for p in user.personas if p.is_public]

    if context:
        public_personas = [
            p for p in public_personas
            if p.context and p.context.name.lower() == context.lower()
        ]

    return [persona_to_public_response(p) for p in public_personas]


@router.get("/api/personas/{persona_id}", response_model=PersonaPublicResponse)
def get_persona(
    persona_id: int,
    x_access_token: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Get a persona by ID.

    - Public personas are accessible to everyone
    - Private personas require the correct access_token in X-Access-Token header
    """
    persona = db.query(Persona).filter(Persona.id == persona_id).first()
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona not found"
        )

    if persona.is_public:
        return persona_to_public_response(persona)

    if not x_access_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access token required for private personas"
        )

    if x_access_token != persona.access_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid access token"
        )

    return persona_to_public_response(persona)


@router.put("/api/personas/{persona_id}", response_model=PersonaOwnerResponse)
def update_persona(
    persona_id: int,
    persona_data: PersonaUpdate,
    x_access_token: str = Header(...),
    db: Session = Depends(get_db)
):
    """Update a persona (requires access token)"""
    persona = db.query(Persona).filter(Persona.id == persona_id).first()
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona not found"
        )

    if x_access_token != persona.access_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid access token"
        )

    if persona_data.name is not None:
        persona.name = persona_data.name
    if persona_data.is_public is not None:
        persona.is_public = persona_data.is_public
        if persona_data.is_public:
            persona.access_token = None
        else:
            persona.access_token = secrets.token_urlsafe(32)
    if persona_data.context_id is not None:
        context = db.query(Context).filter(Context.id == persona_data.context_id).first()
        if not context:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Context not found"
            )
        persona.context_id = persona_data.context_id
    if persona_data.data is not None:
        persona.data = serialize_persona_data(persona_data.data)

    db.commit()
    db.refresh(persona)
    return persona_to_owner_response(persona)


@router.delete("/api/personas/{persona_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_persona(
    persona_id: int,
    x_access_token: str = Header(...),
    db: Session = Depends(get_db)
):
    """Delete a persona (requires access token)"""
    persona = db.query(Persona).filter(Persona.id == persona_id).first()
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona not found"
        )

    if x_access_token != persona.access_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid access token"
        )

    db.delete(persona)
    db.commit()
    return None


@router.post("/api/personas/{persona_id}/regenerate-token", response_model=PersonaOwnerResponse)
def regenerate_access_token(
    persona_id: int,
    x_access_token: str = Header(...),
    db: Session = Depends(get_db)
):
    """Regenerate access token for a persona (requires current access token)"""
    persona = db.query(Persona).filter(Persona.id == persona_id).first()
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona not found"
        )

    if x_access_token != persona.access_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid access token"
        )

    persona.access_token = secrets.token_urlsafe(32)
    db.commit()
    db.refresh(persona)
    return persona_to_owner_response(persona)
