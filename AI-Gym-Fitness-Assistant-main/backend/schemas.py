"""
backend/schemas.py – Pydantic request/response schemas for the FastAPI backend.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    name: str
    age: int = Field(ge=10, le=100)
    weight_kg: float = Field(gt=0, le=500)
    height_cm: float = Field(gt=0, le=300)
    goal: str = "maintain"        # lose | gain | maintain
    activity_level: str = "moderate"

class UserOut(UserCreate):
    id: int
    created_at: datetime
    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Workout
# ---------------------------------------------------------------------------

class WorkoutCreate(BaseModel):
    user_id: int
    exercise: str
    reps: int = 0
    duration_sec: int = 0
    performance_score: float = 0.0
    posture_issues: str = ""

class WorkoutOut(WorkoutCreate):
    id: int
    session_date: datetime
    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Diet
# ---------------------------------------------------------------------------

class DietLogCreate(BaseModel):
    user_id: int
    meal_name: str
    calories: float = 0.0
    protein_g: float = 0.0
    carbs_g: float = 0.0
    fat_g: float = 0.0

class DietLogOut(DietLogCreate):
    id: int
    log_date: datetime
    model_config = {"from_attributes": True}


class DietPlanRequest(BaseModel):
    weight_kg: float
    height_cm: float
    age: int
    is_male: bool = True
    goal: str = "maintain"
    activity_level: str = "moderate"


# ---------------------------------------------------------------------------
# Habit
# ---------------------------------------------------------------------------

class HabitCreate(BaseModel):
    user_id: int
    workout_done: bool = False
    mood: int = Field(ge=1, le=10, default=5)
    sleep_hours: float = Field(ge=0, le=24, default=7.0)
    stress_level: int = Field(ge=1, le=10, default=5)

class HabitOut(HabitCreate):
    id: int
    record_date: datetime
    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Chatbot
# ---------------------------------------------------------------------------

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    reply: str
    sentiment: str


# ---------------------------------------------------------------------------
# IoT
# ---------------------------------------------------------------------------

class IoTRequest(BaseModel):
    age: int = 25
    fitness_level: str = "moderate"


# ---------------------------------------------------------------------------
# Recommender
# ---------------------------------------------------------------------------

class WorkoutRecommendRequest(BaseModel):
    goal: str = "maintain"
    fitness_level: str = "beginner"
    workout_type: Optional[str] = None
    max_duration: int = 120
    top_n: int = 5

class GymRecommendRequest(BaseModel):
    focus: str = "strength"
    price_tier: Optional[str] = None
    top_n: int = 3
