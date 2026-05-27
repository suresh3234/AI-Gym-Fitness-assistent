"""
backend/main.py – FastAPI application factory.

Start with:
    uvicorn backend.main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.db import init_db
from backend.routers import users, workout, diet, iot, tracker, chatbot, recommender

app = FastAPI(
    title="AI Gym & Fitness Assistant API",
    description="Backend API for the AI-powered fitness ecosystem.",
    version="1.0.0",
)

# Allow requests from the Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialise SQLite tables on startup
@app.on_event("startup")
def on_startup():
    init_db()


# Register all routers
app.include_router(users.router)
app.include_router(workout.router)
app.include_router(diet.router)
app.include_router(iot.router)
app.include_router(tracker.router)
app.include_router(chatbot.router)
app.include_router(recommender.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "AI Gym & Fitness Assistant API is running."}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
