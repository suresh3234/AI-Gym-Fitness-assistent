"""
utils/calorie_tracker.py – TDEE and macro computation utilities.
"""

ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}


def calculate_bmr(weight_kg: float, height_cm: float, age: int, is_male: bool) -> float:
    """Mifflin-St Jeor BMR equation."""
    if is_male:
        return round(10 * weight_kg + 6.25 * height_cm - 5 * age + 5, 1)
    return round(10 * weight_kg + 6.25 * height_cm - 5 * age - 161, 1)


def calculate_tdee(bmr: float, activity_level: str) -> float:
    """Total Daily Energy Expenditure."""
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)
    return round(bmr * multiplier, 1)


def goal_calories(tdee: float, goal: str) -> float:
    """Adjust TDEE based on goal (lose / gain / maintain)."""
    if goal == "lose":
        return round(tdee - 500, 1)
    elif goal == "gain":
        return round(tdee + 300, 1)
    return tdee


def macro_split(calories: float, goal: str) -> dict[str, float]:
    """
    Return macro targets in grams.
    Protein: 30%, Carbs: 40%, Fat: 30% (adjusted slightly by goal).
    """
    if goal == "lose":
        protein_pct, carb_pct, fat_pct = 0.40, 0.35, 0.25
    elif goal == "gain":
        protein_pct, carb_pct, fat_pct = 0.30, 0.45, 0.25
    else:
        protein_pct, carb_pct, fat_pct = 0.30, 0.40, 0.30

    return {
        "protein_g": round((calories * protein_pct) / 4, 1),
        "carbs_g": round((calories * carb_pct) / 4, 1),
        "fat_g": round((calories * fat_pct) / 9, 1),
    }
