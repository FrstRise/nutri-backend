from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timezone

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import UserRegisterRequest, UserLoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: UserRegisterRequest):
    """Create a new user account."""
    db = get_db()
    users = db["users"]

    # Check if email already exists
    existing = await users.find_one({"email": body.email.lower()})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    doc = {
        "name": body.name.strip(),
        "email": body.email.lower(),
        "hashed_password": hash_password(body.password),
        "onboarding_complete": False,
        "profile": None,
        "daily_calories": None,
        "macros": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    result = await users.insert_one(doc)
    user_id = str(result.inserted_id)
    token = create_access_token(user_id)

    return TokenResponse(
        access_token=token,
        user_id=user_id,
        name=doc["name"],
        onboarding_complete=False,
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: UserLoginRequest):
    """Authenticate and return a JWT token."""
    db = get_db()
    users = db["users"]

    user = await users.find_one({"email": body.email.lower()})
    if not user or not verify_password(body.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    user_id = str(user["_id"])
    token = create_access_token(user_id)

    return TokenResponse(
        access_token=token,
        user_id=user_id,
        name=user["name"],
        onboarding_complete=user.get("onboarding_complete", False),
    )
