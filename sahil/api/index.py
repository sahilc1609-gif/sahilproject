"""
Vercel Serverless Function Entrypoint
Exposes the WSGI application 'app' for Vercel deployment.
"""

import sys
import os
import urllib.parse
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


class VercelPathMiddleware:
    """
    WSGI Middleware to restore original request paths forwarded by Vercel rewrites.
    Guarantees Flask routes match regardless of how Vercel passes rewritten URLs.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        query = environ.get("QUERY_STRING", "")
        if "__vercel_path=" in query:
            params = urllib.parse.parse_qs(query)
            if "__vercel_path" in params:
                environ["PATH_INFO"] = params["__vercel_path"][0]
                clean = {k: v for k, v in params.items() if k != "__vercel_path"}
                environ["QUERY_STRING"] = urllib.parse.urlencode(clean, doseq=True)
        elif environ.get("HTTP_X_FORWARDED_URI"):
            environ["PATH_INFO"] = environ["HTTP_X_FORWARDED_URI"].split("?")[0]
        elif environ.get("HTTP_X_MATCHED_PATH"):
            environ["PATH_INFO"] = environ["HTTP_X_MATCHED_PATH"].split("?")[0]
        elif environ.get("PATH_INFO") in ("/api/index", "/api", "/api/index.py"):
            environ["PATH_INFO"] = "/"

        return self.wsgi_app(environ, start_response)


# Wrap Flask WSGI instance with path restoration middleware
app.wsgi_app = VercelPathMiddleware(app.wsgi_app)
