import base64
import os
import secrets

import bcrypt
import httpx
from authlib.jose import jwt
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User

# Cognito config
COGNITO_REGION = os.getenv("COGNITO_REGION", "")
COGNITO_POOL_ID = os.getenv("COGNITO_USER_POOL_ID", "")
COGNITO_CLIENT_ID = os.getenv("COGNITO_APP_CLIENT_ID", "")
COGNITO_CLIENT_SECRET = os.getenv("COGNITO_APP_CLIENT_SECRET", "")
COGNITO_DOMAIN = os.getenv("COGNITO_DOMAIN", "")

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
templates = Jinja2Templates(directory="app/templates")


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against bcrypt hash."""
    return bcrypt.checkpw(password.encode(), hashed.encode())


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
@limiter.limit("10/minute")
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
@limiter.limit("10/minute")
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
    if COGNITO_DOMAIN and COGNITO_CLIENT_ID:
        logout_url = (
            f"https://{COGNITO_DOMAIN}/logout"
            f"?client_id={COGNITO_CLIENT_ID}"
            f"&logout_uri={str(request.base_url).rstrip('/')}"
        )
        return RedirectResponse(url=logout_url, status_code=302)
    return RedirectResponse(url="/", status_code=302)


# --- Cognito OIDC routes ---


def _cognito_redirect_uri(request: Request) -> str:
    return str(request.base_url).rstrip("/") + "/auth/cognito/callback"


def _cognito_authorize_url(request: Request, endpoint: str = "oauth2/authorize") -> str:
    """Build a Cognito authorize/signup URL with state parameter."""
    state = secrets.token_urlsafe(32)
    request.session["cognito_state"] = state
    return (
        f"https://{COGNITO_DOMAIN}/{endpoint}"
        f"?client_id={COGNITO_CLIENT_ID}"
        f"&response_type=code"
        f"&scope=email+openid+phone"
        f"&redirect_uri={_cognito_redirect_uri(request)}"
        f"&state={state}"
    )


@router.get("/login/cognito")
async def cognito_login(request: Request):
    if not COGNITO_DOMAIN or not COGNITO_CLIENT_ID:
        return RedirectResponse(url="/login", status_code=302)
    return RedirectResponse(url=_cognito_authorize_url(request), status_code=302)


@router.get("/signup/cognito")
async def cognito_signup(request: Request):
    if not COGNITO_DOMAIN or not COGNITO_CLIENT_ID:
        return RedirectResponse(url="/signup", status_code=302)
    return RedirectResponse(url=_cognito_authorize_url(request, "signup"), status_code=302)


@router.get("/auth/cognito/callback")
async def cognito_callback(request: Request, db: Session = Depends(get_db)):
    code = request.query_params.get("code")
    state = request.query_params.get("state")

    # Verify state
    if not code or not state or state != request.session.get("cognito_state"):
        return RedirectResponse(url="/login", status_code=302)
    request.session.pop("cognito_state", None)

    # Exchange code for tokens
    token_url = f"https://{COGNITO_DOMAIN}/oauth2/token"
    auth_string = base64.b64encode(f"{COGNITO_CLIENT_ID}:{COGNITO_CLIENT_SECRET}".encode()).decode()

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            token_url,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": _cognito_redirect_uri(request),
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {auth_string}",
            },
        )

    if resp.status_code != 200:
        return RedirectResponse(url="/login", status_code=302)

    tokens = resp.json()
    id_token = tokens.get("id_token")
    if not id_token:
        return RedirectResponse(url="/login", status_code=302)

    # Decode ID token using Cognito's public JWKS
    jwks_url = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_POOL_ID}/.well-known/jwks.json"
    async with httpx.AsyncClient() as jwks_client:
        jwks_resp = await jwks_client.get(jwks_url)
    jwks = jwks_resp.json()
    claims = jwt.decode(id_token, jwks)
    cognito_sub = claims.get("sub")
    email = claims.get("email")

    if not cognito_sub or not email:
        return RedirectResponse(url="/login", status_code=302)

    # Look up by cognito_sub first
    user = db.query(User).filter(User.cognito_sub == cognito_sub).first()
    if user:
        request.session["user_id"] = user.id
        return RedirectResponse(url="/dashboard", status_code=302)

    # Look up by email — link existing local account
    user = db.query(User).filter(User.email == email).first()
    if user:
        user.cognito_sub = cognito_sub
        db.commit()
        request.session["user_id"] = user.id
        return RedirectResponse(url="/dashboard", status_code=302)

    # New user — need username
    request.session["cognito_sub"] = cognito_sub
    request.session["cognito_email"] = email
    return RedirectResponse(url="/auth/cognito/complete", status_code=302)


@router.get("/auth/cognito/complete")
async def cognito_complete_page(request: Request):
    if not request.session.get("cognito_sub"):
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse(
        request, "auth/cognito_complete.html",
        {"user": None, "email": request.session.get("cognito_email", "")}
    )


@router.post("/auth/cognito/complete")
async def cognito_complete(
    request: Request,
    username: str = Form(...),
    db: Session = Depends(get_db),
):
    cognito_sub = request.session.get("cognito_sub")
    email = request.session.get("cognito_email")
    if not cognito_sub or not email:
        return RedirectResponse(url="/login", status_code=302)

    # Check username taken
    if db.query(User).filter(User.username == username).first():
        return templates.TemplateResponse(
            request, "auth/cognito_complete.html",
            {"user": None, "email": email, "error": "Username already taken", "username": username}
        )

    user = User(
        email=email,
        username=username,
        cognito_sub=cognito_sub,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Clean up session and log in
    request.session.pop("cognito_sub", None)
    request.session.pop("cognito_email", None)
    request.session["user_id"] = user.id
    return RedirectResponse(url="/dashboard", status_code=302)
