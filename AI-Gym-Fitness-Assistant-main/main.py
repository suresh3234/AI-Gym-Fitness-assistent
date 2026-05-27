"""
main.py – Unified entry point for the AI Gym & Fitness Assistant.

Usage:
    python main.py --mode backend    # Start FastAPI server
    python main.py --mode frontend   # Start Streamlit app
    python main.py --mode both       # Start both (requires two terminals or subprocess)
"""
import argparse
import subprocess
import sys


def start_backend():
    """Launch the FastAPI backend with Uvicorn."""
    print("Starting FastAPI backend on http://127.0.0.1:8000 …")
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "backend.main:app",
         "--host", "0.0.0.0", "--port", "8000", "--reload"],
        check=True,
    )


def start_frontend():
    """Launch the Streamlit frontend."""
    print("Starting Streamlit frontend on http://localhost:8501 …")
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", "frontend/app.py",
         "--server.port", "8501", "--server.address", "0.0.0.0"],
        check=True,
    )


def start_both():
    """Start backend and frontend concurrently."""
    import threading

    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()

    # Give backend a moment to initialise before frontend loads
    import time
    time.sleep(2)

    start_frontend()  # Blocks until Streamlit is stopped


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Gym & Fitness Assistant launcher")
    parser.add_argument(
        "--mode",
        choices=["backend", "frontend", "both"],
        default="frontend",
        help="Which service to start (default: frontend)",
    )
    args = parser.parse_args()

    if args.mode == "backend":
        start_backend()
    elif args.mode == "frontend":
        start_frontend()
    else:
        start_both()
