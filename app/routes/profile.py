import json

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def get_current_user(request: Request, db: Session) -> User | None:
    """Get current user from session."""
    user_id = request.session.get("user_id")
    if user_id:
        return db.query(User).filter(User.id == user_id).first()
    return None


def deserialize_persona_data(data: str | None) -> dict | None:
    """Convert JSON string to dict."""
    if data is None:
        return None
    return json.loads(data)


@router.get("/u/{username}")
async def public_profile(
    request: Request,
    username: str,
    context: str | None = None,
    db: Session = Depends(get_db)
):
    current_user = get_current_user(request, db)

    profile_user = db.query(User).filter(User.username == username).first()
    if not profile_user:
        return templates.TemplateResponse(
            request, "profile.html",
            {
                "user": current_user,
                "profile_user": {"username": username},
                "personas": [],
                "available_contexts": [],
                "context_filter": None,
                "not_found": True
            },
            status_code=404
        )

    # Only show public personas
    public_personas = [p for p in profile_user.personas if p.is_public]

    # Collect unique context names from public personas (for filter buttons)
    available_contexts = sorted(set(
        p.context.name for p in public_personas if p.context
    ))

    # Filter by context name if provided
    if context:
        public_personas = [
            p for p in public_personas
            if p.context and p.context.name.lower() == context.lower()
        ]

    personas = []
    for p in public_personas:
        persona_dict = {
            "id": p.id,
            "name": p.name,
            "is_public": p.is_public,
            "context": p.context,
            "data": deserialize_persona_data(p.data),
        }
        personas.append(persona_dict)

    return templates.TemplateResponse(
        request, "profile.html",
        {
            "user": current_user,
            "profile_user": profile_user,
            "personas": personas,
            "available_contexts": available_contexts,
            "context_filter": context,
        }
    )


@router.get("/u/{username}/{persona_id}")
async def public_persona_detail(
    request: Request,
    username: str,
    persona_id: int,
    db: Session = Depends(get_db)
):
    current_user = get_current_user(request, db)

    profile_user = db.query(User).filter(User.username == username).first()
    if not profile_user:
        return templates.TemplateResponse(
            request, "profile.html",
            {
                "user": current_user,
                "profile_user": {"username": username},
                "personas": [],
                "available_contexts": [],
                "context_filter": None,
                "not_found": True
            },
            status_code=404
        )

    # Find the public persona by ID (must belong to this user)
    persona = next(
        (p for p in profile_user.personas
         if p.is_public and p.id == persona_id),
        None
    )

    if not persona:
        return templates.TemplateResponse(
            request, "profile.html",
            {
                "user": current_user,
                "profile_user": profile_user,
                "personas": [],
                "available_contexts": [],
                "context_filter": None,
                "not_found": True
            },
            status_code=404
        )

    persona_dict = {
        "name": persona.name,
        "context": persona.context,
        "data": deserialize_persona_data(persona.data),
    }

    return templates.TemplateResponse(
        request, "persona/detail.html",
        {
            "user": current_user,
            "profile_user": profile_user,
            "persona": persona_dict,
        }
    )
