"""
backend/routers/recommender.py – Gym & Workout Recommender endpoints.
"""
from fastapi import APIRouter
from backend.schemas import WorkoutRecommendRequest, GymRecommendRequest
from models.gym_recommender import GymRecommender

router = APIRouter(prefix="/recommender", tags=["Recommender"])
rec = GymRecommender()


@router.post("/workouts")
def recommend_workouts(payload: WorkoutRecommendRequest):
    """Return personalised workout recommendations."""
    return rec.recommend_workouts(
        goal=payload.goal,
        fitness_level=payload.fitness_level,
        workout_type=payload.workout_type,
        max_duration=payload.max_duration,
        top_n=payload.top_n,
    )


@router.post("/gyms")
def recommend_gyms(payload: GymRecommendRequest):
    """Return gym recommendations matching user preferences."""
    return rec.recommend_gyms(
        focus=payload.focus,
        price_tier=payload.price_tier,
        top_n=payload.top_n,
    )
