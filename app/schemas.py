from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ============== User Schemas ==============

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserWithPersonas(UserResponse):
    personas: list["PersonaPublicResponse"] = []


# ============== Persona Schemas ==============

class PersonaBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    is_public: bool = False
    data: Optional[dict[str, Any]] = None


class PersonaCreate(PersonaBase):
    pass


class PersonaUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_public: Optional[bool] = None
    data: Optional[dict[str, Any]] = None


class PersonaPublicResponse(BaseModel):
    """Response for public personas - no access_token exposed"""
    id: int
    user_id: int
    name: str
    is_public: bool
    data: Optional[dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PersonaOwnerResponse(PersonaPublicResponse):
    """Response for persona owner - includes access_token"""
    access_token: Optional[str] = None


# ============== Error Schemas ==============

class ErrorResponse(BaseModel):
    detail: str


# Rebuild models for forward references
UserWithPersonas.model_rebuild()
