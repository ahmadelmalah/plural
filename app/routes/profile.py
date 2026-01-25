import json

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
async def public_profile(request: Request, username: str, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)

    profile_user = db.query(User).filter(User.username == username).first()
    if not profile_user:
        return templates.TemplateResponse(
            request, "profile.html",
            {
                "user": current_user,
                "profile_user": {"username": username},
                "personas": [],
                "not_found": True
            },
            status_code=404
        )

    # Only show public personas
    public_personas = [p for p in profile_user.personas if p.is_public]

    personas = []
    for p in public_personas:
        persona_dict = {
            "id": p.id,
            "name": p.name,
            "is_public": p.is_public,
            "data": deserialize_persona_data(p.data),
        }
        personas.append(persona_dict)

    return templates.TemplateResponse(
        request, "profile.html",
        {
            "user": current_user,
            "profile_user": profile_user,
            "personas": personas
        }
    )
