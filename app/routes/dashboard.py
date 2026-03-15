import json
import secrets
from typing import List

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Context, Persona, User

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


def serialize_persona_data(data: dict | None) -> str | None:
    """Convert dict to JSON string."""
    if data is None:
        return None
    return json.dumps(data)


@router.get("/dashboard")
async def dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    # Get all personas with deserialized data
    personas = []
    for p in user.personas:
        persona_dict = {
            "id": p.id,
            "name": p.name,
            "is_public": p.is_public,
            "context": p.context,
            "data": deserialize_persona_data(p.data),
            "access_token": p.access_token,
        }
        personas.append(persona_dict)

    return templates.TemplateResponse(
        request, "dashboard.html",
        {"user": user, "personas": personas}
    )


@router.get("/personas/new")
async def create_persona_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    contexts = db.query(Context).order_by(Context.name).all()
    return templates.TemplateResponse(
        request, "persona/create.html",
        {"user": user, "contexts": contexts}
    )


@router.post("/personas/new")
async def create_persona(
    request: Request,
    name: str = Form(...),
    context_id: int = Form(...),
    is_public: str = Form(None),
    data_keys: List[str] = Form([]),
    data_values: List[str] = Form([]),
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    # Build data dict from key-value pairs
    data = {}
    for key, value in zip(data_keys, data_values):
        if key.strip() and value.strip():
            data[key.strip()] = value.strip()

    persona = Persona(
        user_id=user.id,
        name=name,
        context_id=context_id,
        is_public=is_public == "true",
        data=serialize_persona_data(data) if data else None,
    )
    db.add(persona)
    db.commit()

    return RedirectResponse(url="/dashboard", status_code=302)


@router.get("/personas/{persona_id}/edit")
async def edit_persona_page(request: Request, persona_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    persona = db.query(Persona).filter(Persona.id == persona_id, Persona.user_id == user.id).first()
    if not persona:
        return RedirectResponse(url="/dashboard", status_code=302)

    persona_dict = {
        "id": persona.id,
        "name": persona.name,
        "is_public": persona.is_public,
        "context_id": persona.context_id,
        "data": deserialize_persona_data(persona.data),
        "access_token": persona.access_token,
    }

    contexts = db.query(Context).order_by(Context.name).all()
    return templates.TemplateResponse(
        request, "persona/edit.html",
        {"user": user, "persona": persona_dict, "contexts": contexts}
    )


@router.post("/personas/{persona_id}/edit")
async def edit_persona(
    request: Request,
    persona_id: int,
    name: str = Form(...),
    context_id: int = Form(...),
    is_public: str = Form(None),
    data_keys: List[str] = Form([]),
    data_values: List[str] = Form([]),
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    persona = db.query(Persona).filter(Persona.id == persona_id, Persona.user_id == user.id).first()
    if not persona:
        return RedirectResponse(url="/dashboard", status_code=302)

    # Build data dict from key-value pairs
    data = {}
    for key, value in zip(data_keys, data_values):
        if key.strip() and value.strip():
            data[key.strip()] = value.strip()

    persona.name = name
    persona.context_id = context_id
    persona.is_public = is_public == "true"
    persona.data = serialize_persona_data(data) if data else None
    db.commit()

    return RedirectResponse(url="/dashboard", status_code=302)


@router.post("/personas/{persona_id}/delete")
async def delete_persona(request: Request, persona_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    persona = db.query(Persona).filter(Persona.id == persona_id, Persona.user_id == user.id).first()
    if persona:
        db.delete(persona)
        db.commit()

    return RedirectResponse(url="/dashboard", status_code=302)


@router.post("/personas/{persona_id}/regenerate-token")
async def regenerate_token(request: Request, persona_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    persona = db.query(Persona).filter(Persona.id == persona_id, Persona.user_id == user.id).first()
    if persona:
        persona.access_token = secrets.token_urlsafe(32)
        db.commit()

    return RedirectResponse(url=f"/personas/{persona_id}/edit", status_code=302)
