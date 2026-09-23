"""
Results Management Module
Handles subject marks addition, updates, deletions, and computing
total marks, percentage, grade, and pass/fail status.
"""

import sqlite3
from src.database import get_connection, init_db, load_config
from src.students import get_student_by_roll_no


def get_grading_rules():
    """Retrieve grading thresholds and passing percentage from configuration."""
    config = load_config()
    rules = config.get("grading_rules", {})
    passing_pct = rules.get("passing_percentage", 40.0)
    subject_pass_pct = rules.get("minimum_subject_pass_percentage", 35.0)
    scale = rules.get("grade_scale", [
        {"grade": "A+", "min_percentage": 90.0, "description": "Outstanding"},
        {"grade": "A",  "min_percentage": 80.0, "description": "Excellent"},
        {"grade": "B+", "min_percentage": 70.0, "description": "Very Good"},
        {"grade": "B",  "min_percentage": 60.0, "description": "Good"},
        {"grade": "C",  "min_percentage": 50.0, "description": "Above Average"},
        {"grade": "P",  "min_percentage": 40.0, "description": "Pass"},
        {"grade": "F",  "min_percentage": 0.0,  "description": "Fail"}
    ])
    return passing_pct, subject_pass_pct, scale


def compute_grade_and_status(percentage, failed_subjects_count=0):
    """
    Computes letter grade and pass/fail status based on aggregate percentage
    and individual subject results.
    """
    passing_pct, _, scale = get_grading_rules()

    if failed_subjects_count > 0 or percentage < passing_pct:
        return "F", "FAIL"

    # Sort descending by threshold
    sorted_scale = sorted(scale, key=lambda x: x["min_percentage"], reverse=True)
    for entry in sorted_scale:
        if percentage >= entry["min_percentage"] and entry["grade"] != "F":
            return entry["grade"], "PASS"

    return "F", "FAIL"


def add_or_update_subject_marks(roll_no, subject_name, marks_obtained, max_marks=100.0, db_path=None):
    """
    Add or update marks for a particular subject for a student.
    """
    init_db(db_path)
    student_res = get_student_by_roll_no(roll_no, db_path)
    if not student_res["success"]:
        return student_res

    student = student_res["data"]
    subject_name = str(subject_name).strip()

    if not subject_name:
        return {"success": False, "error": "Subject name cannot be empty."}

    try:
        marks = float(marks_obtained)
        max_m = float(max_marks)
        if max_m <= 0:
            return {"success": False, "error": "Maximum marks must be greater than 0."}
        if marks < 0 or marks > max_m:
            return {"success": False, "error": f"Marks obtained ({marks}) must be between 0 and {max_m}."}
    except (ValueError, TypeError):
        return {"success": False, "error": "Marks must be numeric."}

    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        # UPSERT pattern (Insert or Update if already exists)
        cursor.execute("""
            INSERT INTO results (student_id, subject_name, marks_obtained, max_marks)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(student_id, subject_name) DO UPDATE SET
                marks_obtained = excluded.marks_obtained,
                max_marks = excluded.max_marks,
                updated_at = CURRENT_TIMESTAMP
        """, (student["id"], subject_name, marks, max_m))
        conn.commit()
        return {
            "success": True,
            "message": f"Marks for '{subject_name}' recorded successfully for {student['name']}.",
            "data": {
                "roll_no": roll_no,
                "subject_name": subject_name,
                "marks_obtained": marks,
                "max_marks": max_m
            }
        }
    except Exception as e:
        return {"success": False, "error": f"Database error: {str(e)}"}
    finally:
        conn.close()


def delete_subject_marks(roll_no, subject_name, db_path=None):
    """
    Delete a specific subject result for a student.
    """
    init_db(db_path)
    student_res = get_student_by_roll_no(roll_no, db_path)
    if not student_res["success"]:
        return student_res

    student = student_res["data"]
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            DELETE FROM results
            WHERE student_id = ? AND LOWER(subject_name) = LOWER(?)
        """, (student["id"], str(subject_name).strip()))
        conn.commit()
        if cursor.rowcount > 0:
            return {
                "success": True,
                "message": f"Subject '{subject_name}' deleted for Roll No '{roll_no}'."
            }
        return {
            "success": False,
            "error": f"Subject '{subject_name}' not found for Roll No '{roll_no}'."
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to delete subject: {str(e)}"}
    finally:
        conn.close()


def get_student_result(roll_no, db_path=None):
    """
    Calculate and retrieve complete result report for a student:
    - Student demographic information
    - List of subjects with marks, percentage, and subject pass status
    - Total marks obtained, total max marks
    - Overall percentage
    - Computed Grade
    - Final Pass/Fail status
    """
    init_db(db_path)
    student_res = get_student_by_roll_no(roll_no, db_path)
    if not student_res["success"]:
        return student_res

    student = student_res["data"]
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, subject_name, marks_obtained, max_marks, updated_at
        FROM results
        WHERE student_id = ?
        ORDER BY subject_name ASC
    """, (student["id"],))
    rows = cursor.fetchall()
    conn.close()

    _, subject_pass_pct, _ = get_grading_rules()

    subject_results = []
    total_obtained = 0.0
    total_max = 0.0
    failed_count = 0

    for row in rows:
        m = float(row["marks_obtained"])
        mx = float(row["max_marks"])
        pct = round((m / mx) * 100, 2) if mx > 0 else 0.0
        subj_status = "PASS" if pct >= subject_pass_pct else "FAIL"
        if subj_status == "FAIL":
            failed_count += 1

        total_obtained += m
        total_max += mx

        subject_results.append({
            "subject_name": row["subject_name"],
            "marks_obtained": m,
            "max_marks": mx,
            "percentage": pct,
            "status": subj_status
        })

    num_subjects = len(subject_results)
    if num_subjects > 0 and total_max > 0:
        overall_percentage = round((total_obtained / total_max) * 100, 2)
        grade, status = compute_grade_and_status(overall_percentage, failed_count)
    else:
        overall_percentage = 0.0
        grade = "N/A"
        status = "NO_MARKS_RECORDED"

    return {
        "success": True,
        "data": {
            "student": student,
            "subjects": subject_results,
            "summary": {
                "subjects_count": num_subjects,
                "total_marks_obtained": round(total_obtained, 2),
                "total_max_marks": round(total_max, 2),
                "percentage": overall_percentage,
                "grade": grade,
                "status": status,
                "failed_subjects_count": failed_count
            }
        }
    }


def get_all_results_summary(db_path=None):
    """
    Retrieve summary of results for all students registered in the system.
    """
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT roll_no FROM students ORDER BY roll_no ASC")
    rolls = [r["roll_no"] for r in cursor.fetchall()]
    conn.close()

    summaries = []
    for roll in rolls:
        res = get_student_result(roll, db_path)
        if res["success"]:
            summaries.append({
                "roll_no": res["data"]["student"]["roll_no"],
                "name": res["data"]["student"]["name"],
                "course": res["data"]["student"]["course"],
                "semester": res["data"]["student"]["semester"],
                "total_obtained": res["data"]["summary"]["total_marks_obtained"],
                "total_max": res["data"]["summary"]["total_max_marks"],
                "percentage": res["data"]["summary"]["percentage"],
                "grade": res["data"]["summary"]["grade"],
                "status": res["data"]["summary"]["status"]
            })

    return {"success": True, "count": len(summaries), "data": summaries}
