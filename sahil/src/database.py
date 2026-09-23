"""
Database Management Module
Handles SQLite connection, schema creation, transactions, and indexing.
Also provides cloud-ready abstractions for serverless storage.
"""

import sqlite3
import os
import json
from pathlib import Path

# Resolve base project directory
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "data", "results.db")
CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.example.json")


def load_config():
    """Load configuration from config/config.example.json if available."""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def get_db_path(custom_path=None):
    """Retrieve database path from parameter, environment, config, or default."""
    if custom_path:
        return custom_path

    # Check if running in a Serverless cloud environment (Vercel, AWS Lambda)
    # where the deployment directory is strictly read-only and /tmp is the writable storage.
    if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        tmp_db = "/tmp/results.db"
        if not os.path.exists(tmp_db):
            base_db = os.path.join(BASE_DIR, "data", "results.db")
            if os.path.exists(base_db):
                try:
                    import shutil
                    os.makedirs("/tmp", exist_ok=True)
                    shutil.copy2(base_db, tmp_db)
                except Exception:
                    pass
        return tmp_db

    env_path = os.environ.get("RESULTS_DB_PATH")
    if env_path:
        return env_path
    config = load_config()
    db_config_path = config.get("database", {}).get("path")
    if db_config_path:
        return os.path.join(BASE_DIR, db_config_path)
    return DEFAULT_DB_PATH


def get_connection(db_path=None):
    """
    Establish and return a SQLite database connection with row factory
    and foreign key enforcement enabled.
    """
    target_path = get_db_path(db_path)
    try:
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
    except Exception:
        pass

    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path=None):
    """
    Initialize SQLite database tables and indexes if they do not already exist.
    Creates:
      - students table
      - results table (with CASCADE delete)
      - index on roll_no and student_id
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()

    # Create students table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_no TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        course TEXT NOT NULL,
        semester INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Create results table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        subject_name TEXT NOT NULL,
        marks_obtained REAL NOT NULL,
        max_marks REAL NOT NULL DEFAULT 100.0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
        UNIQUE (student_id, subject_name)
    );
    """)

    # Create indexes for optimal search and join performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_roll_no ON students(roll_no);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_student_id ON results(student_id);")

    conn.commit()
    conn.close()


def reset_db(db_path=None):
    """Drop and recreate all tables (useful for fresh resets and testing)."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS results;")
    cursor.execute("DROP TABLE IF EXISTS students;")
    conn.commit()
    conn.close()
    init_db(db_path)


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", get_db_path())
