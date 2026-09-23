"""
Student Result Management System - Unified Application Entry Point
Supports:
  1. Flask Web Application (exposing WSGI 'app' for Flask, Vercel, Gunicorn)
  2. CLI Application & Argument Execution (when invoked as script)
"""

import sys
import os
from pathlib import Path

# Add repository root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Expose Flask application instance for Flask / Vercel / WSGI
from src.server import app

if __name__ == "__main__":
    from src.app import main
    main()
