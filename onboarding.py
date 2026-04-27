from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime, timezone
from bson import ObjectId

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.user import OnboardingRequest, OnboardingResponse, MacroTargets
from app.services.nutrition import calculate_nutrition_targets

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


@router.post("/complete", response_model=OnboardingResponse)
async def complete_onboarding(
    body: OnboardingRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Save the user's onboarding profile and calculate personalised
    calorie + macro targets. Requires a valid JWT in the Authorization header.
    """
    db = get_db()
    users = db["users"]

    # Verify user exists
    user = await users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    # Calculate personalised nutrition targets
    targets = calculate_nutrition_targets(
        weight_kg=body.weight,
        height_cm=body.height,
        age=body.age,
        gender=body.gender,
        activity=body.activity,
        goal=body.goal,
    )

    # Persist to MongoDB
    await users.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "onboarding_complete": True,
                "profile": body.model_dump(),
                "daily_calories": targets["daily_calories"],
                "macros": targets["macros"],
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )

    return OnboardingResponse(
        message="Profile saved successfully!",
        daily_calories=targets["daily_calories"],
        macros=MacroTargets(**targets["macros"]),
    )


@router.get("/profile")
async def get_profile(user_id: str = Depends(get_current_user_id)):
    """Return the current user's stored profile and nutrition targets."""
    db = get_db()
    users = db["users"]

    user = await users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    return {
        "name": user["name"],
        "email": user["email"],
        "onboarding_complete": user.get("onboarding_complete", False),
        "profile": user.get("profile"),
        "daily_calories": user.get("daily_calories"),
        "macros": user.get("macros"),
    }
