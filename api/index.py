"""Vercel entry point.

Vercel sends every browser and API request to this FastAPI application. The
actual product code remains in backend/app so it can also run locally.
"""

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.main import app  # noqa: E402
