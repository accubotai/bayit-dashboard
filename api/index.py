"""Vercel serverless entry point — imports FastAPI app from backend/."""

import sys
from pathlib import Path

# Add project root to Python path so `backend` is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.main import app  # noqa: E402, F401
