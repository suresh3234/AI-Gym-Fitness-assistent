"""
models/performance_analyzer.py – Pose-to-Performance Analyzer.

Scores workout efficiency and tracks weekly progress based on
rep counts, duration, and posture quality.
"""
import math
from datetime import datetime, timedelta


class PerformanceAnalyzer:
    """Generates performance scores and weekly progress reports."""

    # Expected rep ranges per minute for each exercise
    EXPECTED_RPM = {
        "Bicep Curl": 15,
        "Squat": 12,
        "Push-up": 20,
        "Lunge": 12,
        "Plank": 1,          # reps don't apply – use duration proxy
    }

    # ---------------------------------------------------------------------------

    def score_session(
        self,
        exercise: str,
        reps: int,
        duration_sec: int,
        posture_issues: list[str],
    ) -> dict:
        """
        Compute a 0-100 performance score for a single session.

        Components:
        - Volume score  (40 pts): reps vs. expected RPM for the duration
        - Form score    (40 pts): penalise posture issues
        - Effort score  (20 pts): reps × weight proxy (always 1 here)
        """
        if duration_sec == 0:
            return {"score": 0, "grade": "F", "breakdown": {}}

        expected_reps = max(1, (duration_sec / 60) * self.EXPECTED_RPM.get(exercise, 12))
        volume_score = min(40, round(40 * (reps / expected_reps), 1))

        # Penalise 5 points per distinct posture issue, min 0
        form_penalty = min(40, len(set(posture_issues)) * 8)
        form_score = max(0, 40 - form_penalty)

        # Effort: reward high rep rate
        rpm_actual = (reps / duration_sec) * 60
        rpm_expected = self.EXPECTED_RPM.get(exercise, 12)
        effort_score = min(20, round(20 * (rpm_actual / rpm_expected), 1))

        total = round(volume_score + form_score + effort_score, 1)

        return {
            "score": total,
            "grade": self._grade(total),
            "breakdown": {
                "volume": volume_score,
                "form": form_score,
                "effort": effort_score,
            },
        }

    @staticmethod
    def _grade(score: float) -> str:
        if score >= 90:
            return "A"
        elif score >= 75:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 40:
            return "D"
        return "F"

    # ---------------------------------------------------------------------------

    def weekly_progress(self, sessions: list[dict]) -> dict:
        """
        Aggregate session data into a weekly progress summary.
        Each session dict: {exercise, reps, duration_sec, performance_score, session_date}.
        """
        if not sessions:
            return {
                "total_sessions": 0,
                "total_reps": 0,
                "total_duration_min": 0,
                "avg_score": 0,
                "best_score": 0,
                "exercises": {},
                "daily_scores": {},
            }

        total_reps = sum(s.get("reps", 0) for s in sessions)
        total_dur = sum(s.get("duration_sec", 0) for s in sessions)
        scores = [s.get("performance_score", 0) for s in sessions]
        avg_score = round(sum(scores) / len(scores), 1)
        best_score = max(scores)

        # Per-exercise breakdown
        exercises: dict[str, dict] = {}
        for s in sessions:
            ex = s.get("exercise", "Unknown")
            if ex not in exercises:
                exercises[ex] = {"sessions": 0, "total_reps": 0, "avg_score": 0, "_scores": []}
            exercises[ex]["sessions"] += 1
            exercises[ex]["total_reps"] += s.get("reps", 0)
            exercises[ex]["_scores"].append(s.get("performance_score", 0))

        for ex, data in exercises.items():
            data["avg_score"] = round(sum(data["_scores"]) / len(data["_scores"]), 1)
            del data["_scores"]

        # Daily score mapping
        daily: dict[str, list[float]] = {}
        for s in sessions:
            date = s.get("session_date", datetime.utcnow())
            if isinstance(date, datetime):
                key = date.date().isoformat()
            else:
                key = str(date)[:10]
            daily.setdefault(key, []).append(s.get("performance_score", 0))

        daily_avg = {d: round(sum(v) / len(v), 1) for d, v in daily.items()}

        return {
            "total_sessions": len(sessions),
            "total_reps": total_reps,
            "total_duration_min": round(total_dur / 60, 1),
            "avg_score": avg_score,
            "best_score": best_score,
            "exercises": exercises,
            "daily_scores": daily_avg,
        }

    def improvement_tips(self, avg_score: float, exercise: str) -> list[str]:
        """Return targeted improvement tips based on score."""
        tips = []
        if avg_score < 50:
            tips.append(f"Work on your {exercise} form before increasing reps.")
            tips.append("Consider recording yourself to spot technique errors.")
        elif avg_score < 75:
            tips.append("Good foundation! Now focus on adding volume gradually.")
            tips.append("Try slowing down the eccentric phase for better muscle engagement.")
        else:
            tips.append("Excellent performance! Look into progressive overload strategies.")
            tips.append("Consider adding accessory exercises to complement your main lifts.")
        return tips
