"""
Nutrition calculation service.
Uses the Mifflin-St Jeor equation for BMR, then applies an activity multiplier
to get TDEE (Total Daily Energy Expenditure), and finally adjusts for goal.
"""

ACTIVITY_MULTIPLIERS = {
    "Sedentary": 1.2,
    "Lightly Active": 1.375,
    "Moderate": 1.55,
    "Very Active": 1.725,
}

GOAL_ADJUSTMENTS = {
    "loss": -500,      # caloric deficit
    "maintain": 0,
    "gain": +300,      # lean bulk surplus
}

# Macro ratios (protein / carbs / fat) — as percentage of calories
MACRO_RATIOS = {
    "loss":     {"protein": 0.35, "carbs": 0.40, "fat": 0.25},
    "maintain": {"protein": 0.30, "carbs": 0.45, "fat": 0.25},
    "gain":     {"protein": 0.30, "carbs": 0.50, "fat": 0.20},
}

CALORIES_PER_GRAM = {"protein": 4, "carbs": 4, "fat": 9}


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """Mifflin-St Jeor BMR formula."""
    if gender == "male":
        return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    elif gender == "female":
        return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    else:
        # Average of male and female for 'other'
        male = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
        female = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
        return (male + female) / 2


def calculate_nutrition_targets(
    weight_kg: float,
    height_cm: float,
    age: int,
    gender: str,
    activity: str,
    goal: str,
) -> dict:
    """
    Returns daily calorie target + macro breakdown in grams.
    """
    bmr = calculate_bmr(weight_kg, height_cm, age, gender)
    tdee = bmr * ACTIVITY_MULTIPLIERS.get(activity, 1.2)
    target_calories = round(tdee + GOAL_ADJUSTMENTS.get(goal, 0))

    # Clamp to safe minimum
    target_calories = max(target_calories, 1200)

    ratios = MACRO_RATIOS[goal]
    protein_g = round((target_calories * ratios["protein"]) / CALORIES_PER_GRAM["protein"])
    carbs_g = round((target_calories * ratios["carbs"]) / CALORIES_PER_GRAM["carbs"])
    fat_g = round((target_calories * ratios["fat"]) / CALORIES_PER_GRAM["fat"])

    return {
        "daily_calories": target_calories,
        "macros": {
            "protein_g": protein_g,
            "carbs_g": carbs_g,
            "fat_g": fat_g,
        },
    }
