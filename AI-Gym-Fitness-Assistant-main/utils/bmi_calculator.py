"""
utils/bmi_calculator.py – BMI and related body composition utilities.
"""


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Return BMI rounded to two decimal places."""
    height_m = height_cm / 100.0
    return round(weight_kg / (height_m ** 2), 2)


def bmi_category(bmi: float) -> str:
    """Return the WHO BMI category string."""
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25.0:
        return "Normal weight"
    elif bmi < 30.0:
        return "Overweight"
    else:
        return "Obese"


def ideal_weight_range(height_cm: float) -> tuple[float, float]:
    """Return the healthy weight range (kg) for a given height (cm)."""
    height_m = height_cm / 100.0
    low = round(18.5 * height_m ** 2, 1)
    high = round(24.9 * height_m ** 2, 1)
    return low, high


def body_fat_estimate(bmi: float, age: int, is_male: bool) -> float:
    """
    Estimate body-fat percentage using the Deurenberg formula.
    body_fat = (1.20 * bmi) + (0.23 * age) - (10.8 * sex) - 5.4
    where sex = 1 for male, 0 for female.
    """
    sex = 1 if is_male else 0
    bf = (1.20 * bmi) + (0.23 * age) - (10.8 * sex) - 5.4
    return round(max(bf, 0.0), 1)
