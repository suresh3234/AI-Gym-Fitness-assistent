"""
models/diet_planner.py – AI Dietician & Calorie Coach.

Recommends meal plans based on BMI, calorie targets, and dietary preferences.
"""
import random

from utils.calorie_tracker import calculate_bmr, calculate_tdee, goal_calories, macro_split
from utils.bmi_calculator import calculate_bmi, bmi_category

# ---------------------------------------------------------------------------
# Meal database (simple in-memory catalogue)
# ---------------------------------------------------------------------------

MEALS = {
    "breakfast": [
        {"name": "Oatmeal with banana", "calories": 350, "protein_g": 12, "carbs_g": 60, "fat_g": 6},
        {"name": "Greek yoghurt with berries", "calories": 200, "protein_g": 18, "carbs_g": 25, "fat_g": 3},
        {"name": "Scrambled eggs on toast", "calories": 420, "protein_g": 22, "carbs_g": 38, "fat_g": 16},
        {"name": "Protein smoothie", "calories": 300, "protein_g": 30, "carbs_g": 35, "fat_g": 5},
        {"name": "Avocado toast with eggs", "calories": 480, "protein_g": 20, "carbs_g": 42, "fat_g": 24},
    ],
    "lunch": [
        {"name": "Grilled chicken salad", "calories": 450, "protein_g": 40, "carbs_g": 20, "fat_g": 18},
        {"name": "Brown rice & lentil bowl", "calories": 520, "protein_g": 22, "carbs_g": 80, "fat_g": 8},
        {"name": "Tuna wrap", "calories": 400, "protein_g": 35, "carbs_g": 45, "fat_g": 10},
        {"name": "Quinoa vegetable bowl", "calories": 430, "protein_g": 18, "carbs_g": 65, "fat_g": 10},
        {"name": "Paneer tikka wrap", "calories": 490, "protein_g": 28, "carbs_g": 50, "fat_g": 18},
    ],
    "dinner": [
        {"name": "Baked salmon with veggies", "calories": 480, "protein_g": 45, "carbs_g": 20, "fat_g": 22},
        {"name": "Chicken stir-fry with rice", "calories": 550, "protein_g": 42, "carbs_g": 60, "fat_g": 12},
        {"name": "Dal tadka with roti", "calories": 500, "protein_g": 20, "carbs_g": 70, "fat_g": 12},
        {"name": "Tofu & vegetable curry", "calories": 420, "protein_g": 22, "carbs_g": 50, "fat_g": 14},
        {"name": "Turkey meatballs with pasta", "calories": 590, "protein_g": 48, "carbs_g": 62, "fat_g": 14},
    ],
    "snack": [
        {"name": "Mixed nuts (30 g)", "calories": 180, "protein_g": 5, "carbs_g": 8, "fat_g": 15},
        {"name": "Protein bar", "calories": 200, "protein_g": 20, "carbs_g": 22, "fat_g": 6},
        {"name": "Apple with peanut butter", "calories": 220, "protein_g": 6, "carbs_g": 30, "fat_g": 10},
        {"name": "Cottage cheese (100 g)", "calories": 110, "protein_g": 14, "carbs_g": 4, "fat_g": 4},
        {"name": "Hard-boiled eggs (2)", "calories": 155, "protein_g": 13, "carbs_g": 1, "fat_g": 11},
    ],
}


class DietPlanner:
    """Generates personalised meal plans and diet recommendations."""

    def get_diet_plan(
        self,
        weight_kg: float,
        height_cm: float,
        age: int,
        is_male: bool,
        goal: str,
        activity_level: str,
    ) -> dict:
        """
        Return a full daily diet plan with calorie and macro targets.
        *goal*: 'lose' | 'gain' | 'maintain'
        *activity_level*: 'sedentary' | 'light' | 'moderate' | 'active' | 'very_active'
        """
        bmi = calculate_bmi(weight_kg, height_cm)
        category = bmi_category(bmi)
        bmr = calculate_bmr(weight_kg, height_cm, age, is_male)
        tdee = calculate_tdee(bmr, activity_level)
        target_cals = goal_calories(tdee, goal)
        macros = macro_split(target_cals, goal)

        # Pick one meal per slot
        plan = {slot: random.choice(options) for slot, options in MEALS.items()}
        total_cals = sum(m["calories"] for m in plan.values())

        return {
            "bmi": bmi,
            "bmi_category": category,
            "bmr": bmr,
            "tdee": tdee,
            "target_calories": target_cals,
            "macros": macros,
            "meal_plan": plan,
            "meal_plan_calories": total_cals,
        }

    def recommend_meal(self, slot: str, max_calories: float = 600) -> dict:
        """Return a random meal for *slot* that fits within *max_calories*."""
        options = [m for m in MEALS.get(slot, MEALS["snack"]) if m["calories"] <= max_calories]
        if not options:
            options = MEALS.get(slot, MEALS["snack"])
        return random.choice(options)

    def get_all_meals(self, slot: str) -> list[dict]:
        """Return all available meals for a given slot."""
        return MEALS.get(slot, [])

    def diet_tip(self, goal: str) -> str:
        """Return a context-aware diet tip."""
        tips = {
            "lose": [
                "Focus on protein to preserve muscle while in a calorie deficit.",
                "Eat more fibre-rich vegetables to feel full longer.",
                "Avoid liquid calories – stick to water and black coffee.",
            ],
            "gain": [
                "Add calorie-dense foods like nuts, dairy, and whole grains.",
                "Eat every 3-4 hours to keep muscle protein synthesis elevated.",
                "Don't skip breakfast – it sets the tone for your calorie intake.",
            ],
            "maintain": [
                "Stick to whole foods 80% of the time and enjoy treats in moderation.",
                "Hydration is key – aim for 2-3 litres of water daily.",
                "Balance your macros across all meals for steady energy.",
            ],
        }
        return random.choice(tips.get(goal, tips["maintain"]))
