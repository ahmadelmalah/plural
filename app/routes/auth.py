import hashlib

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
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


def hash_password(password: str) -> str:
    """Simple password hashing using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    return hash_password(password) == hashed


def get_current_user(request: Request, db: Session) -> User | None:
    """Get current user from session."""
    user_id = request.session.get("user_id")
    if user_id:
        return db.query(User).filter(User.id == user_id).first()
    return None


@router.get("/login")
async def login_page(request: Request):
    user = get_current_user(request, next(get_db()))
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse(request, "auth/login.html", {"user": None})


@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()

    if not user or not user.password_hash:
        return templates.TemplateResponse(
            request, "auth/login.html",
            {"user": None, "error": "Invalid email or password"}
        )

    if not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            request, "auth/login.html",
            {"user": None, "error": "Invalid email or password"}
        )

    request.session["user_id"] = user.id
    return RedirectResponse(url="/dashboard", status_code=302)


@router.get("/signup")
async def signup_page(request: Request):
    user = get_current_user(request, next(get_db()))
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse(request, "auth/signup.html", {"user": None})


@router.post("/signup")
async def signup(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Check if email exists
    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse(
            request, "auth/signup.html",
            {"user": None, "error": "Email already registered", "username": username, "email": email}
        )

    # Check if username exists
    if db.query(User).filter(User.username == username).first():
        return templates.TemplateResponse(
            request, "auth/signup.html",
            {"user": None, "error": "Username already taken", "username": username, "email": email}
        )

    # Create user
    user = User(
        email=email,
        username=username,
        password_hash=hash_password(password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    request.session["user_id"] = user.id
    return RedirectResponse(url="/dashboard", status_code=302)


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)
