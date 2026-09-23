"""
Students Management Module
Handles student registration, retrieval, updating, deletion, and validation.
Serverless-ready functions return clean dictionaries.
"""

import re
import sqlite3
from src.database import get_connection, init_db

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"


def validate_student_input(roll_no, name, email, course, semester):
    """
    Validates student fields.
    Returns (True, None) if valid, or (False, error_message) if invalid.
    """
    if not roll_no or not str(roll_no).strip():
        return False, "Roll number cannot be empty."
    if not name or not str(name).strip():
        return False, "Student name cannot be empty."
    if not email or not re.match(EMAIL_REGEX, str(email).strip()):
        return False, f"Invalid email format: '{email}'."
    if not course or not str(course).strip():
        return False, "Course name cannot be empty."
    try:
        sem = int(semester)
        if sem < 1 or sem > 12:
            return False, "Semester must be an integer between 1 and 12."
    except (ValueError, TypeError):
        return False, "Semester must be a valid integer."

    return True, None


def register_student(roll_no, name, email, course, semester, db_path=None):
    """
    Register a new student in the database.
    """
    init_db(db_path)
    roll_no = str(roll_no).strip().upper()
    name = str(name).strip()
    email = str(email).strip().lower()
    course = str(course).strip()

    is_valid, error = validate_student_input(roll_no, name, email, course, semester)
    if not is_valid:
        return {"success": False, "error": error}

    conn = get_connection(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO students (roll_no, name, email, course, semester)
            VALUES (?, ?, ?, ?, ?)
        """, (roll_no, name, email, course, int(semester)))
        conn.commit()
        student_id = cursor.lastrowid
        return {
            "success": True,
            "message": f"Student '{name}' (Roll No: {roll_no}) registered successfully.",
            "data": {
                "id": student_id,
                "roll_no": roll_no,
                "name": name,
                "email": email,
                "course": course,
                "semester": int(semester)
            }
        }
    except sqlite3.IntegrityError:
        return {
            "success": False,
            "error": f"Student with Roll Number '{roll_no}' already exists."
        }
    except Exception as e:
        return {"success": False, "error": f"Database error: {str(e)}"}
    finally:
        conn.close()


def get_student_by_roll_no(roll_no, db_path=None):
    """
    Fetch a student record by roll number.
    """
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE roll_no = ?", (str(roll_no).strip().upper(),))
        row = cursor.fetchone()
        if row:
            return {"success": True, "data": dict(row)}
        return {"success": False, "error": f"Student with Roll No '{roll_no}' not found."}
    finally:
        conn.close()


def get_student_by_id(student_id, db_path=None):
    """
    Fetch a student record by internal primary key ID.
    """
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
        row = cursor.fetchone()
        if row:
            return {"success": True, "data": dict(row)}
        return {"success": False, "error": f"Student with ID '{student_id}' not found."}
    finally:
        conn.close()


def list_all_students(db_path=None):
    """
    Retrieve all registered students ordered by roll number.
    """
    try:
        init_db(db_path)
        conn = get_connection(db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students ORDER BY roll_no ASC")
            rows = cursor.fetchall()
            students = [dict(row) for row in rows]
            return {"success": True, "count": len(students), "data": students}
        finally:
            conn.close()
    except Exception as e:
        return {"success": False, "error": f"Failed to list students: {str(e)}", "data": []}


def update_student(roll_no, name=None, email=None, course=None, semester=None, db_path=None):
    """
    Update details of an existing student.
    """
    init_db(db_path)
    roll_no = str(roll_no).strip().upper()
    existing = get_student_by_roll_no(roll_no, db_path)
    if not existing["success"]:
        return existing

    current = existing["data"]
    new_name = str(name).strip() if name is not None else current["name"]
    new_email = str(email).strip().lower() if email is not None else current["email"]
    new_course = str(course).strip() if course is not None else current["course"]
    new_sem = int(semester) if semester is not None else current["semester"]

    is_valid, error = validate_student_input(roll_no, new_name, new_email, new_course, new_sem)
    if not is_valid:
        return {"success": False, "error": error}

    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE students
            SET name = ?, email = ?, course = ?, semester = ?
            WHERE roll_no = ?
        """, (new_name, new_email, new_course, new_sem, roll_no))
        conn.commit()
        return {
            "success": True,
            "message": f"Student '{roll_no}' updated successfully.",
            "data": {
                "roll_no": roll_no,
                "name": new_name,
                "email": new_email,
                "course": new_course,
                "semester": new_sem
            }
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to update student: {str(e)}"}
    finally:
        conn.close()


def delete_student(roll_no, db_path=None):
    """
    Delete a student and all associated result records (cascade).
    Explicitly deletes child results first to guarantee no orphaned rows.
    """
    init_db(db_path)
    roll_no = str(roll_no).strip().upper()
    existing = get_student_by_roll_no(roll_no, db_path)
    if not existing["success"]:
        return existing

    student_id = existing["data"]["id"]
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM results WHERE student_id = ?", (student_id,))
        cursor.execute("DELETE FROM students WHERE roll_no = ?", (roll_no,))
        conn.commit()
        return {
            "success": True,
            "message": f"Student '{roll_no}' and related results deleted successfully."
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to delete student: {str(e)}"}
    finally:
        conn.close()


def search_students(query, db_path=None):
    """
    Search students by roll number, name, or email keyword.
    """
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        keyword = f"%{str(query).strip()}%"
        cursor.execute("""
            SELECT * FROM students
            WHERE roll_no LIKE ? OR name LIKE ? OR email LIKE ?
            ORDER BY roll_no ASC
        """, (keyword, keyword, keyword))
        rows = cursor.fetchall()
        students = [dict(row) for row in rows]
        return {"success": True, "count": len(students), "data": students}
    finally:
        conn.close()
