"""
models/gym_recommender.py – Gym & Workout Recommender System.

Uses content-based filtering to recommend workouts and gyms
based on user preferences, fitness level, and goals.
"""
from __future__ import annotations

import math
from typing import Any


# ---------------------------------------------------------------------------
# Static catalogues
# ---------------------------------------------------------------------------

WORKOUTS: list[dict[str, Any]] = [
    {"id": 1, "name": "Full Body HIIT", "level": "beginner", "goal": ["lose", "maintain"],
     "type": "cardio", "duration_min": 30, "calories_burned": 350, "equipment": "none"},
    {"id": 2, "name": "Strength Training A", "level": "intermediate", "goal": ["gain", "maintain"],
     "type": "strength", "duration_min": 60, "calories_burned": 300, "equipment": "gym"},
    {"id": 3, "name": "Yoga Flow", "level": "beginner", "goal": ["maintain"],
     "type": "flexibility", "duration_min": 45, "calories_burned": 180, "equipment": "mat"},
    {"id": 4, "name": "Advanced Powerlifting", "level": "advanced", "goal": ["gain"],
     "type": "strength", "duration_min": 90, "calories_burned": 400, "equipment": "gym"},
    {"id": 5, "name": "Morning Run 5 km", "level": "intermediate", "goal": ["lose", "maintain"],
     "type": "cardio", "duration_min": 30, "calories_burned": 300, "equipment": "none"},
    {"id": 6, "name": "Upper Body Pump", "level": "intermediate", "goal": ["gain", "maintain"],
     "type": "strength", "duration_min": 50, "calories_burned": 280, "equipment": "gym"},
    {"id": 7, "name": "Core & Abs Circuit", "level": "beginner", "goal": ["lose", "maintain"],
     "type": "strength", "duration_min": 25, "calories_burned": 200, "equipment": "mat"},
    {"id": 8, "name": "Cycling Intervals", "level": "intermediate", "goal": ["lose"],
     "type": "cardio", "duration_min": 40, "calories_burned": 380, "equipment": "bike"},
    {"id": 9, "name": "Olympic Lifting", "level": "advanced", "goal": ["gain"],
     "type": "strength", "duration_min": 75, "calories_burned": 350, "equipment": "gym"},
    {"id": 10, "name": "Pilates Fundamentals", "level": "beginner", "goal": ["maintain", "lose"],
     "type": "flexibility", "duration_min": 40, "calories_burned": 160, "equipment": "mat"},
]

GYMS: list[dict[str, Any]] = [
    {"id": 1, "name": "FitZone Pro", "type": "commercial", "focus": ["strength", "cardio"],
     "price_tier": "mid", "amenities": ["pool", "sauna", "classes"], "rating": 4.5},
    {"id": 2, "name": "Iron Paradise", "type": "powerlifting", "focus": ["strength"],
     "price_tier": "low", "amenities": ["heavy equipment", "chalk"], "rating": 4.7},
    {"id": 3, "name": "Zen Wellness", "type": "wellness", "focus": ["flexibility", "cardio"],
     "price_tier": "high", "amenities": ["spa", "yoga", "meditation"], "rating": 4.6},
    {"id": 4, "name": "CrossFit Box Alpha", "type": "crossfit", "focus": ["cardio", "strength"],
     "price_tier": "mid", "amenities": ["coaching", "community"], "rating": 4.4},
    {"id": 5, "name": "Home Gym Starter Kit", "type": "home", "focus": ["strength", "flexibility"],
     "price_tier": "none", "amenities": ["convenience"], "rating": 4.2},
]


# ---------------------------------------------------------------------------
# Recommender
# ---------------------------------------------------------------------------

class GymRecommender:
    """Content-based recommender for workouts and gyms."""

    def recommend_workouts(
        self,
        goal: str,
        fitness_level: str,
        workout_type: str | None = None,
        max_duration: int = 120,
        top_n: int = 5,
    ) -> list[dict]:
        """
        Score and rank workouts based on user attributes.
        Returns top *top_n* recommendations sorted by relevance score.
        """
        scored = []
        for w in WORKOUTS:
            score = self._workout_score(w, goal, fitness_level, workout_type, max_duration)
            if score > 0:
                scored.append({**w, "relevance": round(score, 2)})

        scored.sort(key=lambda x: x["relevance"], reverse=True)
        return scored[:top_n]

    def _workout_score(
        self,
        workout: dict,
        goal: str,
        level: str,
        w_type: str | None,
        max_dur: int,
    ) -> float:
        """Compute a relevance score (0-1) for a workout."""
        score = 0.0

        # Goal match (40%)
        if goal in workout.get("goal", []):
            score += 0.40

        # Level match (30%)
        level_map = {"beginner": 0, "intermediate": 1, "advanced": 2}
        user_lvl = level_map.get(level, 1)
        work_lvl = level_map.get(workout.get("level", "intermediate"), 1)
        level_diff = abs(user_lvl - work_lvl)
        score += 0.30 * max(0, 1 - level_diff * 0.5)

        # Type match (20%)
        if w_type and workout.get("type") == w_type:
            score += 0.20
        elif not w_type:
            score += 0.10  # no preference – partial credit

        # Duration (10%)
        if workout.get("duration_min", 60) <= max_dur:
            score += 0.10

        return score

    def recommend_gyms(
        self,
        focus: str = "strength",
        price_tier: str | None = None,
        top_n: int = 3,
    ) -> list[dict]:
        """
        Score and rank gyms. Returns top *top_n* results.
        """
        scored = []
        for g in GYMS:
            score = self._gym_score(g, focus, price_tier)
            scored.append({**g, "relevance": round(score, 2)})

        scored.sort(key=lambda x: x["relevance"], reverse=True)
        return scored[:top_n]

    def _gym_score(self, gym: dict, focus: str, price_tier: str | None) -> float:
        """Compute a relevance score for a gym."""
        score = 0.0

        if focus in gym.get("focus", []):
            score += 0.50

        if price_tier and gym.get("price_tier") == price_tier:
            score += 0.30
        elif not price_tier:
            score += 0.15

        # Normalise rating contribution (4-5 star range → 0-0.20)
        rating = gym.get("rating", 4.0)
        score += 0.20 * ((rating - 4.0) / 1.0)

        return score
