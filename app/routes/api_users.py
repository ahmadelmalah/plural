from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Context, User
from app.schemas import (
    ContextResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
    UserWithPersonas,
)
from app.utils import context_to_response, persona_to_public_response

router = APIRouter()


# ============== Context Endpoints ==============

@router.get("/api/contexts", response_model=list[ContextResponse])
def list_contexts(db: Session = Depends(get_db)):
    """List all available contexts"""
    contexts = db.query(Context).order_by(Context.name).all()
    return [context_to_response(c) for c in contexts]


# ============== User Endpoints ==============

@router.post("/api/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

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


@router.get("/api/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    """List all users"""
    users = db.query(User).all()
    return users


@router.get("/api/users/{user_id}", response_model=UserWithPersonas)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a user by ID with their public personas"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

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


@router.put("/api/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    """Update a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user_data.email and user_data.email != user.email:
        existing = db.query(User).filter(User.email == user_data.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        user.email = user_data.email

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


@router.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
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
