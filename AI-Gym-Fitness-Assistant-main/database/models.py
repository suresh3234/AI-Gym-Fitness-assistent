"""
database/models.py – ORM models for users, workouts, diet logs, and habit records.
"""
from datetime import datetime

from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, Text

from database.db import Base


class User(Base):
    """Stores basic user profile information."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    weight_kg = Column(Float, nullable=False)
    height_cm = Column(Float, nullable=False)
    goal = Column(String(50), default="maintain")  # lose / gain / maintain
    activity_level = Column(String(50), default="moderate")
    created_at = Column(DateTime, default=datetime.utcnow)


class WorkoutSession(Base):
    """Logs individual workout sessions with rep counts and scores."""
    __tablename__ = "workout_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    exercise = Column(String(100), nullable=False)
    reps = Column(Integer, default=0)
    duration_sec = Column(Integer, default=0)
    performance_score = Column(Float, default=0.0)
    posture_issues = Column(Text, default="")
    session_date = Column(DateTime, default=datetime.utcnow)


class DietLog(Base):
    """Tracks daily calorie and macronutrient intake."""
    __tablename__ = "diet_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    meal_name = Column(String(200), nullable=False)
    calories = Column(Float, default=0.0)
    protein_g = Column(Float, default=0.0)
    carbs_g = Column(Float, default=0.0)
    fat_g = Column(Float, default=0.0)
    log_date = Column(DateTime, default=datetime.utcnow)


class HabitRecord(Base):
    """Records daily habit check-ins for behavioral tracking."""
    __tablename__ = "habit_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    workout_done = Column(Boolean, default=False)
    mood = Column(Integer, default=5)          # 1-10 scale
    sleep_hours = Column(Float, default=7.0)
    stress_level = Column(Integer, default=5)  # 1-10 scale
    record_date = Column(DateTime, default=datetime.utcnow)
