from dotenv import load_dotenv

load_dotenv()

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqladmin import Admin
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from app.admin import ContextAdmin, PersonaAdmin, UserAdmin
from app.database import engine, get_db
from app.models import User
from app.routes import api_personas, api_users, auth, dashboard, profile

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

app = FastAPI(
    title="Plural - Identity Management API",
    description="A centralized API for managing multidimensional digital identities through Personas",
    version="0.1.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Session middleware for auth
app.add_middleware(SessionMiddleware, secret_key="plural-secret-key-change-in-production")

# Static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Include routes
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(profile.router)
app.include_router(api_users.router)
app.include_router(api_personas.router)

# Admin panel
admin = Admin(app, engine, title="Plural Admin")
admin.add_view(UserAdmin)
admin.add_view(PersonaAdmin)
admin.add_view(ContextAdmin)


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
