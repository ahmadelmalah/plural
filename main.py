import json
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqladmin import Admin
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from app.admin import PersonaAdmin, UserAdmin
from app.database import SessionLocal, engine
from app.models import Persona, User
from app.routes import auth, dashboard, profile
from app.schemas import (
    ErrorResponse,
    PersonaCreate,
    PersonaOwnerResponse,
    PersonaPublicResponse,
    PersonaUpdate,
    UserCreate,
    UserResponse,
    UserUpdate,
    UserWithPersonas,
)

app = FastAPI(
    title="Plural - Identity Management API",
    description="A centralized API for managing multidimensional digital identities through Personas",
    version="0.1.0",
)

# Session middleware for auth
app.add_middleware(SessionMiddleware, secret_key="plural-secret-key-change-in-production")

# Static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Include web routes
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(profile.router)

# Admin panel
admin = Admin(app, engine, title="Plural Admin")
admin.add_view(UserAdmin)
admin.add_view(PersonaAdmin)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============== Helper Functions ==============

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


def persona_to_public_response(persona: Persona) -> PersonaPublicResponse:
    """Convert Persona model to public response (no access_token)"""
    return PersonaPublicResponse(
        id=persona.id,
        user_id=persona.user_id,
        name=persona.name,
        is_public=persona.is_public,
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
        data=deserialize_persona_data(persona.data),
        access_token=persona.access_token,
        created_at=persona.created_at,
        updated_at=persona.updated_at,
    )


# ============== Root ==============

def get_current_user_for_template(request: Request, db: Session) -> User | None:
    """Get current user from session for templates."""
    user_id = request.session.get("user_id")
    if user_id:
        return db.query(User).filter(User.id == user_id).first()
    return None


@app.get("/")
async def root(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_for_template(request, db)
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse(request, "index.html", {"user": user})


# ============== User Endpoints ==============

@app.post("/api/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username already exists
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    user = User(email=user_data.email, username=user_data.username)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.get("/api/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    """List all users"""
    users = db.query(User).all()
    return users


@app.get("/api/users/{user_id}", response_model=UserWithPersonas)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a user by ID with their public personas"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Only include public personas in the response
    public_personas = [
        persona_to_public_response(p) for p in user.personas if p.is_public
    ]

    return UserWithPersonas(
        id=user.id,
        email=user.email,
        username=user.username,
        created_at=user.created_at,
        updated_at=user.updated_at,
        personas=public_personas,
    )


@app.put("/api/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    """Update a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check for email conflicts
    if user_data.email and user_data.email != user.email:
        existing = db.query(User).filter(User.email == user_data.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        user.email = user_data.email

    # Check for username conflicts
    if user_data.username and user_data.username != user.username:
        existing = db.query(User).filter(User.username == user_data.username).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        user.username = user_data.username

    db.commit()
    db.refresh(user)
    return user


@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user and all their personas (cascade)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db.delete(user)
    db.commit()
    return None


# ============== Persona Endpoints ==============

@app.post(
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

    persona = Persona(
        user_id=user_id,
        name=persona_data.name,
        is_public=persona_data.is_public,
        data=serialize_persona_data(persona_data.data),
    )
    db.add(persona)
    db.commit()
    db.refresh(persona)
    return persona_to_owner_response(persona)


@app.get("/api/users/{user_id}/personas", response_model=list[PersonaPublicResponse])
def list_user_personas(user_id: int, db: Session = Depends(get_db)):
    """List all public personas for a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Only return public personas
    public_personas = [p for p in user.personas if p.is_public]
    return [persona_to_public_response(p) for p in public_personas]


@app.get("/api/personas/{persona_id}", response_model=PersonaPublicResponse)
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

    # If persona is public, return it
    if persona.is_public:
        return persona_to_public_response(persona)

    # If persona is private, check access token
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


@app.put("/api/personas/{persona_id}", response_model=PersonaOwnerResponse)
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

    # Verify access token
    if x_access_token != persona.access_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid access token"
        )

    if persona_data.name is not None:
        persona.name = persona_data.name
    if persona_data.is_public is not None:
        persona.is_public = persona_data.is_public
    if persona_data.data is not None:
        persona.data = serialize_persona_data(persona_data.data)

    db.commit()
    db.refresh(persona)
    return persona_to_owner_response(persona)


@app.delete("/api/personas/{persona_id}", status_code=status.HTTP_204_NO_CONTENT)
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

    # Verify access token
    if x_access_token != persona.access_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid access token"
        )

    db.delete(persona)
    db.commit()
    return None


@app.post("/api/personas/{persona_id}/regenerate-token", response_model=PersonaOwnerResponse)
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

    # Verify current access token
    if x_access_token != persona.access_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid access token"
        )

    # Generate new token
    import secrets
    persona.access_token = secrets.token_urlsafe(32)
    db.commit()
    db.refresh(persona)
    return persona_to_owner_response(persona)
