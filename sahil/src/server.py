"""
Local Web Server for Serverless Student Result Management System
Provides a modern REST API and serves the dashboard UI on localhost.
"""

import os
import sys
import json
import socket
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database import init_db, get_db_path
from src.students import (
    register_student,
    get_student_by_roll_no,
    list_all_students,
    update_student,
    delete_student,
    search_students
)
from src.results import (
    add_or_update_subject_marks,
    delete_subject_marks,
    get_student_result,
    get_all_results_summary
)
from src.app import seed_sample_data

template_dir = PROJECT_ROOT / "templates"
if not template_dir.exists():
    template_dir = Path.cwd() / "templates"

static_dir = PROJECT_ROOT / "static"
if not static_dir.exists():
    static_dir = Path.cwd() / "static"

app = Flask(
    __name__,
    template_folder=str(template_dir),
    static_folder=str(static_dir)
)


def is_port_available(port, host="127.0.0.1"):
    """Check if a port is free on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) != 0


# ============================================================================
# Web Page Route
# ============================================================================

@app.route("/")
@app.route("/api")
@app.route("/api/index")
def index():
    return render_template("index.html")


# ============================================================================
# REST API Endpoints
# ============================================================================

@app.route("/api/students", methods=["GET"])
def api_list_or_search_students():
    query = request.args.get("search", "").strip()
    if query:
        res = search_students(query)
    else:
        res = list_all_students()
    return jsonify(res), (200 if res.get("success") else 400)


@app.route("/api/students", methods=["POST"])
def api_register_student():
    data = request.get_json() or {}
    res = register_student(
        roll_no=data.get("roll_no"),
        name=data.get("name"),
        email=data.get("email"),
        course=data.get("course"),
        semester=data.get("semester")
    )
    code = 201 if res.get("success") else 400
    return jsonify(res), code


@app.route("/api/students/<roll_no>", methods=["GET"])
def api_get_student(roll_no):
    res = get_student_by_roll_no(roll_no)
    code = 200 if res.get("success") else 404
    return jsonify(res), code


@app.route("/api/students/<roll_no>", methods=["PUT"])
def api_update_student(roll_no):
    data = request.get_json() or {}
    res = update_student(
        roll_no=roll_no,
        name=data.get("name"),
        email=data.get("email"),
        course=data.get("course"),
        semester=data.get("semester")
    )
    code = 200 if res.get("success") else 400
    return jsonify(res), code


@app.route("/api/students/<roll_no>", methods=["DELETE"])
def api_delete_student(roll_no):
    res = delete_student(roll_no)
    code = 200 if res.get("success") else 404
    return jsonify(res), code


@app.route("/api/results/<roll_no>", methods=["GET"])
def api_get_student_result(roll_no):
    res = get_student_result(roll_no)
    code = 200 if res.get("success") else 404
    return jsonify(res), code


@app.route("/api/results/<roll_no>", methods=["POST"])
def api_add_marks(roll_no):
    data = request.get_json() or {}
    res = add_or_update_subject_marks(
        roll_no=roll_no,
        subject_name=data.get("subject_name"),
        marks_obtained=data.get("marks_obtained"),
        max_marks=data.get("max_marks", 100.0)
    )
    code = 200 if res.get("success") else 400
    return jsonify(res), code


@app.route("/api/results/<roll_no>/<path:subject_name>", methods=["DELETE"])
def api_delete_marks(roll_no, subject_name):
    res = delete_subject_marks(roll_no, subject_name)
    code = 200 if res.get("success") else 404
    return jsonify(res), code


@app.route("/api/summary", methods=["GET"])
def api_summary():
    res = get_all_results_summary()
    return jsonify(res), 200


@app.route("/api/seed", methods=["POST"])
def api_seed():
    success = seed_sample_data()
    if success:
        return jsonify({"success": True, "message": "Sample data seeded successfully."}), 200
    return jsonify({"success": False, "error": "Failed to seed sample data."}), 500


def run_server(port=None, host="127.0.0.1", debug=False):
    """Start local web server on an available port."""
    init_db()
    if port is None:
        if is_port_available(5050, host):
            port = 5050
        elif is_port_available(5000, host):
            port = 5000
        elif is_port_available(8000, host):
            port = 8000
        else:
            port = 8080

    print("=" * 65)
    print(" SERVERLESS STUDENT RESULT MANAGEMENT SYSTEM - WEB DASHBOARD ".center(65))
    print("=" * 65)
    print(f"[*] Local URL: http://{host}:{port}/")
    print(f"[*] REST API:  http://{host}:{port}/api/summary")
    print(f"[*] Database:  {get_db_path()}")
    print("=" * 65)
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run Student Result Management System Web Dashboard")
    parser.add_argument("--port", type=int, default=None, help="Port to bind (default: auto 5050/5000)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host address")
    parser.add_argument("--debug", action="store_true", help="Enable Flask debug mode")
    args = parser.parse_args()
    run_server(port=args.port, host=args.host, debug=args.debug)
