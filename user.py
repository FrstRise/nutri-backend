from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def utc_now() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Auth models
# ---------------------------------------------------------------------------

class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    name: str
    onboarding_complete: bool


# ---------------------------------------------------------------------------
# Onboarding / Profile models
# ---------------------------------------------------------------------------

class OnboardingRequest(BaseModel):
    age: int = Field(..., ge=10, le=120)
    gender: Literal["male", "female", "other"]
    height: float = Field(..., ge=50, le=300, description="Height in cm")
    weight: float = Field(..., ge=20, le=500, description="Weight in kg")
    goal: Literal["loss", "gain", "maintain"]
    activity: Literal["Sedentary", "Lightly Active", "Moderate", "Very Active"]


class OnboardingResponse(BaseModel):
    message: str
    daily_calories: int
    macros: MacroTargets


class MacroTargets(BaseModel):
    protein_g: int
    carbs_g: int
    fat_g: int


# ---------------------------------------------------------------------------
# Internal DB document shape (not exposed to API consumers)
# ---------------------------------------------------------------------------

class UserDocument(BaseModel):
    """Mirrors what we store in MongoDB users collection."""
    name: str
    email: str
    hashed_password: str
    onboarding_complete: bool = False
    profile: Optional[dict] = None        # raw onboarding data
    daily_calories: Optional[int] = None
    macros: Optional[dict] = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
