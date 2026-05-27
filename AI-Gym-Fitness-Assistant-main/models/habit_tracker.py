"""
models/habit_tracker.py – Fitness Habit Tracker with Behavioural AI.

Trains a simple ML model to predict whether a user is likely to skip
their workout based on mood, sleep, and stress data, then sends a
targeted motivational nudge.
"""
import random

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler

from utils.helpers import get_motivational_message


class HabitTracker:
    """
    Tracks habit records and predicts workout-skip probability using
    a Gradient Boosting classifier trained on synthetic data.

    Feature vector: [mood (1-10), sleep_hours, stress_level (1-10)]
    Label: 1 = skipped workout, 0 = completed workout
    """

    def __init__(self):
        self.scaler = StandardScaler()
        self.model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        self._trained = False
        self._train_on_synthetic()

    # ------------------------------------------------------------------
    # Model training
    # ------------------------------------------------------------------

    def _generate_synthetic_data(self, n: int = 500):
        """
        Generate synthetic training data with realistic correlations:
        - Low mood + high stress + little sleep → likely to skip.
        """
        rng = np.random.default_rng(seed=42)
        mood = rng.integers(1, 11, size=n).astype(float)
        sleep = rng.uniform(4, 10, size=n)
        stress = rng.integers(1, 11, size=n).astype(float)

        # Logistic-style probability of skipping
        log_odds = -0.5 * mood + 0.6 * stress - 0.4 * sleep + 1.5
        prob_skip = 1 / (1 + np.exp(-log_odds))
        labels = (rng.uniform(size=n) < prob_skip).astype(int)

        X = np.column_stack([mood, sleep, stress])
        return X, labels

    def _train_on_synthetic(self):
        """Fit the model on synthetic data so predictions work out of the box."""
        X, y = self._generate_synthetic_data()
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self._trained = True

    # ------------------------------------------------------------------
    # Prediction & advice
    # ------------------------------------------------------------------

    def predict_skip_probability(
        self, mood: int, sleep_hours: float, stress_level: int
    ) -> float:
        """
        Return the probability (0-1) that the user will skip today's workout.
        """
        features = np.array([[mood, sleep_hours, stress_level]], dtype=float)
        scaled = self.scaler.transform(features)
        prob = self.model.predict_proba(scaled)[0][1]  # class=1 probability
        return round(float(prob), 3)

    def get_nudge(self, skip_prob: float) -> str:
        """Return a motivational nudge tailored to skip probability."""
        if skip_prob > 0.70:
            messages = [
                "Your stats suggest you might skip today – but you've got this! Even 15 minutes counts.",
                "High stress detected. A short workout can be your stress relief today!",
                "We know it's tough. Start with just a warm-up – momentum will carry you.",
            ]
        elif skip_prob > 0.40:
            messages = [
                "You're on the fence today – push through! Future you will be grateful.",
                "Moderate risk of skipping. Put on your shoes and go – that's step one!",
                get_motivational_message(),
            ]
        else:
            messages = [
                "You're in great shape mentally – crush that workout today!",
                "Excellent readiness score! Time to hit a personal best.",
                "Low skip risk – your consistency is paying off!",
            ]
        return random.choice(messages)

    def weekly_summary(self, records: list[dict]) -> dict:
        """
        Compute a weekly habit summary from a list of HabitRecord-like dicts.
        Each dict should have: workout_done, mood, sleep_hours, stress_level.
        """
        if not records:
            return {"workouts_completed": 0, "avg_mood": 0, "avg_sleep": 0,
                    "avg_stress": 0, "completion_rate": 0.0}

        workouts = sum(1 for r in records if r.get("workout_done"))
        avg_mood = round(sum(r.get("mood", 5) for r in records) / len(records), 1)
        avg_sleep = round(sum(r.get("sleep_hours", 7) for r in records) / len(records), 1)
        avg_stress = round(sum(r.get("stress_level", 5) for r in records) / len(records), 1)
        rate = round(workouts / len(records) * 100, 1)

        return {
            "workouts_completed": workouts,
            "avg_mood": avg_mood,
            "avg_sleep": avg_sleep,
            "avg_stress": avg_stress,
            "completion_rate": rate,
        }
