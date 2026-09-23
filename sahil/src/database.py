"""
Database Management Module
Handles SQLite connection, schema creation, transactions, indexing, and WAL mode.
Provides cloud-ready abstractions for serverless storage (Vercel, AWS Lambda)
and eliminates locking bottlenecks.
"""

import sqlite3
import os
import json
import shutil
from pathlib import Path

# Resolve base project directory
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "data", "results.db")
CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.json")
CONFIG_EXAMPLE_PATH = os.path.join(BASE_DIR, "config", "config.example.json")

# In-memory tracking of initialized databases to prevent redundant DDL execution
_INITIALIZED_PATHS = set()


def load_config():
    """Load configuration from config/config.json or config.example.json if available."""
    for p in (CONFIG_PATH, CONFIG_EXAMPLE_PATH):
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return {}


def get_db_path(custom_path=None):
    """Retrieve database path from parameter, environment, config, or default."""
    if custom_path:
        return custom_path

    # Check if running in a Serverless cloud environment (Vercel, AWS Lambda)
    # where the deployment directory is strictly read-only and /tmp is writable.
    if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        tmp_db = "/tmp/results.db"
        # If tmp_db does not exist or has 0 bytes, copy from bundled data/results.db
        if not os.path.exists(tmp_db) or os.path.getsize(tmp_db) == 0:
            os.makedirs("/tmp", exist_ok=True)
            base_db = os.path.join(BASE_DIR, "data", "results.db")
            if os.path.exists(base_db) and os.path.getsize(base_db) > 0:
                try:
                    shutil.copy2(base_db, tmp_db)
                except Exception as e:
                    print(f"[Database] Warning copying base DB to /tmp: {e}")
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
    Establish and return a robust SQLite connection configured with:
      - Safe parent directory verification
      - 30-second busy timeout to prevent 'database is locked' errors
      - check_same_thread=False for multi-threaded Flask server
      - Row factory enabled (dictionary-like access)
      - Foreign key constraints enforced
      - MEMORY journal mode in serverless (/tmp) to avoid .shm/.wal lockouts;
        WAL mode for local concurrent multi-threaded execution
    """
    target_path = get_db_path(db_path)
    dir_name = os.path.dirname(target_path)
    if dir_name:
        try:
            os.makedirs(dir_name, exist_ok=True)
        except Exception:
            pass

    conn = sqlite3.connect(
        target_path,
        timeout=30.0,
        check_same_thread=False,
        isolation_level=None  # autocommit mode; explicit transactions via BEGIN
    )
    conn.row_factory = sqlite3.Row

    # Performance and concurrency optimizations
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA busy_timeout = 30000;")
        if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
            # Serverless environments (/tmp) perform best with MEMORY journal mode
            conn.execute("PRAGMA journal_mode = MEMORY;")
        else:
            conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
    except Exception:
        pass

    return conn


def init_db(db_path=None, force=False):
    """
    Initialize SQLite database tables, constraints, and indexes.
    Caches initialization state to prevent repetitive table creation queries.
    """
    target_path = get_db_path(db_path)

    # Skip redundant DDL calls if already initialized and DB file exists
    if not force and target_path in _INITIALIZED_PATHS and os.path.exists(target_path):
        return

    conn = get_connection(db_path)
    cursor = conn.cursor()

    try:
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

        _INITIALIZED_PATHS.add(target_path)
    finally:
        conn.close()


def check_db_health(db_path=None):
    """
    Perform a complete database health check and integrity test.
    Automatically initializes schema if needed.
    Returns status dict with table counts and integrity status.
    """
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA integrity_check;")
        integrity_row = cursor.fetchone()
        integrity = integrity_row[0] if integrity_row else "ok"

        cursor.execute("SELECT COUNT(*) FROM students;")
        student_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM results;")
        result_count = cursor.fetchone()[0]

        return {
            "status": "healthy" if integrity == "ok" else "error",
            "integrity": integrity,
            "student_count": student_count,
            "result_count": result_count,
            "path": get_db_path(db_path)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "path": get_db_path(db_path)
        }
    finally:
        conn.close()


def reset_db(db_path=None):
    """Drop and recreate all tables (useful for fresh resets and testing)."""
    target_path = get_db_path(db_path)
    _INITIALIZED_PATHS.discard(target_path)

    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("DROP TABLE IF EXISTS results;")
        cursor.execute("DROP TABLE IF EXISTS students;")
    finally:
        conn.close()

    init_db(db_path, force=True)


if __name__ == "__main__":
    init_db(force=True)
    health = check_db_health()
    print("Database initialized and verified:")
    print(json.dumps(health, indent=2))
