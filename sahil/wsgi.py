"""
WSGI Application Entry Point
Enables standard 'python -m flask run' and WSGI server deployment.
"""

import sys
import os
from pathlib import Path

# Add repository root directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database import init_db
from src.server import app

# Ensure database is initialized
init_db()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=True)
