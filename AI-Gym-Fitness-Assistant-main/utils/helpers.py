"""
utils/helpers.py – General-purpose utility functions shared across modules.
"""
import random
from datetime import datetime, timedelta


MOTIVATIONAL_MESSAGES = [
    "Every rep counts – keep pushing!",
    "Consistency beats perfection. Show up today.",
    "Your only competition is yesterday's you.",
    "The pain you feel today is the strength you'll feel tomorrow.",
    "Don't stop when you're tired – stop when you're done.",
    "Small steps every day lead to big results.",
    "Believe in yourself and your fitness journey!",
    "You are one workout away from a good mood.",
    "Discipline is doing it even when you don't feel like it.",
    "Your future self will thank you for today's effort.",
]


def get_motivational_message() -> str:
    """Return a random motivational message."""
    return random.choice(MOTIVATIONAL_MESSAGES)


def generate_week_dates(weeks_back: int = 1) -> list[str]:
    """Return a list of date strings for the past N weeks."""
    today = datetime.utcnow().date()
    return [(today - timedelta(days=i)).isoformat() for i in range(weeks_back * 7 - 1, -1, -1)]


def clamp(value: float, low: float, high: float) -> float:
    """Clamp a value between low and high."""
    return max(low, min(high, value))


def percentage(part: float, total: float) -> float:
    """Return what percentage *part* is of *total* (0-100)."""
    if total == 0:
        return 0.0
    return round((part / total) * 100, 1)


def format_duration(seconds: int) -> str:
    """Convert seconds to a human-readable MM:SS string."""
    minutes, secs = divmod(int(seconds), 60)
    return f"{minutes:02d}:{secs:02d}"
