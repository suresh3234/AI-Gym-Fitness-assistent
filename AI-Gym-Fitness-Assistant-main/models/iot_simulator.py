"""
models/iot_simulator.py – Smart Gym Assistant (IoT Simulation).

Simulates sensor data (heart rate, calories burned, equipment load)
and adjusts workout intensity recommendations accordingly.
"""
import random
import time
from dataclasses import dataclass, field


@dataclass
class SensorReading:
    """Simulated IoT sensor snapshot."""
    heart_rate: int          # bpm
    calories_burned: float   # kcal since session start
    equipment_load: int      # % of max resistance
    temperature_c: float     # ambient gym temperature
    session_duration_sec: int
    timestamp: float = field(default_factory=time.time)


class IoTSimulator:
    """Generates simulated gym sensor data and intensity recommendations."""

    # Heart-rate zones (bpm)
    ZONES = {
        "resting":       (0, 60),
        "warm_up":       (61, 100),
        "fat_burn":      (101, 130),
        "cardio":        (131, 160),
        "peak":          (161, 185),
        "max_effort":    (186, 220),
    }

    def __init__(self, age: int = 25, fitness_level: str = "moderate"):
        self.age = age
        self.fitness_level = fitness_level
        self._session_start = time.time()
        self._last_hr = 75
        self._calories = 0.0
        self._load = 50

    # ------------------------------------------------------------------

    def _max_hr(self) -> int:
        return 220 - self.age

    def _simulate_heart_rate(self) -> int:
        """Drift heart rate realistically within a ±8 bpm range."""
        delta = random.randint(-8, 8)
        self._last_hr = max(50, min(self._max_hr(), self._last_hr + delta))
        return self._last_hr

    def _simulate_calories(self, hr: int, delta_sec: int = 5) -> float:
        """Estimate incremental calories burned (MET approximation)."""
        met = 0.0014 * hr - 0.03
        increment = met * (70 / 60) * (delta_sec / 60)  # assume 70 kg user
        self._calories = round(self._calories + max(0, increment), 1)
        return self._calories

    def get_reading(self) -> SensorReading:
        """Return a fresh simulated sensor reading."""
        hr = self._simulate_heart_rate()
        duration = int(time.time() - self._session_start)
        cals = self._simulate_calories(hr)
        load = self._simulate_load()
        temp = round(random.uniform(20.0, 26.0), 1)
        return SensorReading(
            heart_rate=hr,
            calories_burned=cals,
            equipment_load=load,
            temperature_c=temp,
            session_duration_sec=duration,
        )

    def _simulate_load(self) -> int:
        """Vary equipment load by ±5%."""
        self._load = max(10, min(100, self._load + random.randint(-5, 5)))
        return self._load

    # ------------------------------------------------------------------
    # Intensity recommendation
    # ------------------------------------------------------------------

    def hr_zone(self, hr: int) -> str:
        """Identify heart-rate training zone."""
        for zone, (low, high) in self.ZONES.items():
            if low <= hr <= high:
                return zone
        return "unknown"

    def recommend_intensity(self, reading: SensorReading) -> dict:
        """
        Analyse sensor data and return an intensity adjustment recommendation.
        """
        zone = self.hr_zone(reading.heart_rate)
        max_hr = self._max_hr()
        hr_pct = round((reading.heart_rate / max_hr) * 100, 1)

        if hr_pct > 90:
            action = "decrease"
            reason = "Heart rate is dangerously high. Reduce intensity immediately."
        elif hr_pct > 80:
            action = "maintain"
            reason = "You are in the peak zone. Sustain this effort."
        elif hr_pct > 65:
            action = "maintain"
            reason = "Optimal cardio zone. Keep going!"
        elif hr_pct > 50:
            action = "increase"
            reason = "Heart rate is low. Push harder to improve fitness."
        else:
            action = "increase"
            reason = "Warm up more before the main workout."

        hydration = "Drink water now!" if reading.session_duration_sec > 1200 else "Stay hydrated."

        return {
            "zone": zone,
            "hr_pct_of_max": hr_pct,
            "action": action,
            "reason": reason,
            "hydration": hydration,
            "suggested_load": min(100, reading.equipment_load + (5 if action == "increase" else -5)),
        }

    def reset(self):
        """Reset session counters."""
        self._session_start = time.time()
        self._calories = 0.0
        self._last_hr = 75
        self._load = 50
