"""
backend/routers/iot.py – Smart Gym Assistant IoT simulation endpoints.
"""
from fastapi import APIRouter
from models.iot_simulator import IoTSimulator
from backend.schemas import IoTRequest

router = APIRouter(prefix="/iot", tags=["IoT"])

# Module-level simulators keyed by age+level (simple cache)
_simulators: dict[str, IoTSimulator] = {}


def _get_simulator(age: int, fitness_level: str) -> IoTSimulator:
    key = f"{age}_{fitness_level}"
    if key not in _simulators:
        _simulators[key] = IoTSimulator(age=age, fitness_level=fitness_level)
    return _simulators[key]


@router.post("/reading")
def get_iot_reading(payload: IoTRequest):
    """Return a simulated sensor reading and intensity recommendation."""
    sim = _get_simulator(payload.age, payload.fitness_level)
    reading = sim.get_reading()
    recommendation = sim.recommend_intensity(reading)
    return {
        "sensor": {
            "heart_rate": reading.heart_rate,
            "calories_burned": reading.calories_burned,
            "equipment_load": reading.equipment_load,
            "temperature_c": reading.temperature_c,
            "session_duration_sec": reading.session_duration_sec,
        },
        "recommendation": recommendation,
    }


@router.post("/reset")
def reset_iot_session(payload: IoTRequest):
    """Reset the IoT session (start fresh)."""
    key = f"{payload.age}_{payload.fitness_level}"
    if key in _simulators:
        _simulators[key].reset()
    return {"status": "reset"}
