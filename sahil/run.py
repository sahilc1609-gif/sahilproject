"""
Quick Launcher for Localhost Web Dashboard
Usage:
  python run.py
  python run.py --port 5050
"""

import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.server import run_server

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Start Serverless Student Result Management System Web App")
    parser.add_argument("--port", type=int, default=None, help="Port to listen on (default 5050)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host interface (default 127.0.0.1)")
    args = parser.parse_args()
    run_server(port=args.port, host=args.host)
