"""
Vercel Serverless Function Entrypoint
Exposes the WSGI application 'app' for Vercel deployment.
"""

import sys
import os
from pathlib import Path

# Add project root directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Flag VERCEL environment for read-only filesystem handling
os.environ["VERCEL"] = "1"

from src.database import init_db
from src.students import list_all_students
from src.app import seed_sample_data
from src.server import app

# Cold start initialization: ensure database and schema exist in /tmp
try:
    init_db()
    existing = list_all_students()
    if not existing.get("data"):
        seed_sample_data()
except Exception as e:
    print(f"[Vercel Init] Database setup note: {e}")

# 'app' is the Flask WSGI instance required by Vercel
