"""
Serverless Student Result Management System - Main Entry Point
Supports:
  1. Interactive Command-Line Interface (CLI)
  2. Direct CLI argument parser
  3. Serverless / AWS Lambda event handlers
"""

import sys
import os
import json
import argparse
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database import init_db, reset_db, get_db_path
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


# ============================================================================
# Formatting Helpers for Console Display
# ============================================================================

def print_header(title):
    """Print an eye-catching terminal header."""
    line = "=" * 68
    print(f"\n{line}")
    print(f" {title.center(66)} ")
    print(f"{line}")


def print_success(msg):
    print(f"[+] SUCCESS: {msg}")


def print_error(msg):
    print(f"[-] ERROR: {msg}")


def print_info(msg):
    print(f"[*] INFO: {msg}")


def format_student_table(students):
    """Format and print a list of students as an aligned table."""
    if not students:
        print("No student records found.")
        return

    header = f"{'ID':<4} | {'Roll No':<12} | {'Name':<22} | {'Course':<20} | {'Sem':<4} | {'Email'}"
    print("-" * len(header))
    print(header)
    print("-" * len(header))
    for s in students:
        print(f"{s.get('id', '-'):<4} | {s.get('roll_no', ''):<12} | {s.get('name', ''):<22} | {s.get('course', ''):<20} | {s.get('semester', ''):<4} | {s.get('email', '')}")
    print("-" * len(header))


def print_result_card(result_data):
    """Print a comprehensive, beautifully structured report card."""
    student = result_data["student"]
    subjects = result_data["subjects"]
    summary = result_data["summary"]

    print_header(f"STUDENT RESULT CARD - {student['roll_no']}")
    print(f" Student Name : {student['name']:<25} Roll Number : {student['roll_no']}")
    print(f" Course       : {student['course']:<25} Semester    : {student['semester']}")
    print(f" Email        : {student['email']}")
    print("-" * 68)
    print(f" {'#':<3} | {'Subject Name':<30} | {'Marks':<7} | {'Max':<5} | {'%':<6} | {'Status'}")
    print("-" * 68)

    if not subjects:
        print("   No subject marks have been recorded for this student yet.")
    else:
        for idx, subj in enumerate(subjects, 1):
            status_symbol = "[PASS]" if subj["status"] == "PASS" else "[FAIL]"
            print(f" {idx:<3} | {subj['subject_name']:<30} | {subj['marks_obtained']:<7.1f} | {subj['max_marks']:<5.1f} | {subj['percentage']:<6.1f} | {status_symbol}")

    print("=" * 68)
    print(f" Total Obtained : {summary['total_marks_obtained']} / {summary['total_max_marks']}")
    print(f" Percentage     : {summary['percentage']:.2f}%")
    print(f" Grade          : {summary['grade']}")
    print(f" Final Status   : {summary['status']}")
    if summary.get("failed_subjects_count", 0) > 0:
        print(f" Warning        : Failed in {summary['failed_subjects_count']} subject(s)!")
    print("=" * 68 + "\n")


def seed_sample_data(sample_file=None):
    """Seed the database with predefined sample data."""
    if not sample_file:
        sample_file = os.path.join(PROJECT_ROOT, "sample", "sample_data.json")

    if not os.path.exists(sample_file):
        print_error(f"Sample data file not found at {sample_file}")
        return False

    with open(sample_file, "r", encoding="utf-8") as f:
        records = json.load(f)

    init_db()
    print_info(f"Seeding {len(records)} sample students and marks...")
    for rec in records:
        reg_res = register_student(
            roll_no=rec["roll_no"],
            name=rec["name"],
            email=rec["email"],
            course=rec["course"],
            semester=rec["semester"]
        )
        if reg_res["success"]:
            print_success(f"Registered: {rec['name']} ({rec['roll_no']})")
        else:
            print_info(f"Student {rec['roll_no']} already present or skipped: {reg_res.get('error')}")

        for subj in rec.get("subjects", []):
            add_or_update_subject_marks(
                roll_no=rec["roll_no"],
                subject_name=subj["subject_name"],
                marks_obtained=subj["marks_obtained"],
                max_marks=subj.get("max_marks", 100.0)
            )

    print_success("Database seeding completed successfully.")
    return True


# ============================================================================
# Interactive CLI Menu
# ============================================================================

def interactive_cli():
    """Runs the primary terminal interactive interface."""
    init_db()
    while True:
        print("\n" + "=" * 60)
        print(" SERVERLESS STUDENT RESULT MANAGEMENT SYSTEM ".center(60, " "))
        print("=" * 60)
        print("  1. Register New Student")
        print("  2. Add / Update Subject Marks")
        print("  3. View Individual Student Result Card")
        print("  4. Search Students (by Roll No, Name, or Email)")
        print("  5. List All Registered Students")
        print("  6. View Class Performance Summary")
        print("  7. Delete a Subject Result")
        print("  8. Delete a Student Record")
        print("  9. Seed Sample Records (sample/sample_data.json)")
        print("  0. Exit")
        print("-" * 60)

        choice = input("Select an option (0-9): ").strip()

        if choice == "1":
            print("\n--- Register Student ---")
            roll_no = input("Roll Number: ").strip()
            name = input("Full Name: ").strip()
            email = input("Email Address: ").strip()
            course = input("Course (e.g. B.Tech CS): ").strip()
            sem = input("Semester (1-12): ").strip()
            res = register_student(roll_no, name, email, course, sem)
            if res["success"]:
                print_success(res["message"])
            else:
                print_error(res["error"])

        elif choice == "2":
            print("\n--- Add / Update Subject Marks ---")
            roll_no = input("Student Roll Number: ").strip()
            subj = input("Subject Name: ").strip()
            marks = input("Marks Obtained: ").strip()
            max_m = input("Maximum Marks [Default: 100]: ").strip() or "100"
            res = add_or_update_subject_marks(roll_no, subj, marks, max_m)
            if res["success"]:
                print_success(res["message"])
            else:
                print_error(res["error"])

        elif choice == "3":
            print("\n--- View Student Result Card ---")
            roll_no = input("Enter Student Roll Number: ").strip()
            res = get_student_result(roll_no)
            if res["success"]:
                print_result_card(res["data"])
            else:
                print_error(res["error"])

        elif choice == "4":
            print("\n--- Search Students ---")
            q = input("Search query: ").strip()
            res = search_students(q)
            if res["success"]:
                print(f"\nFound {res['count']} matching student(s):")
                format_student_table(res["data"])
            else:
                print_error(res["error"])

        elif choice == "5":
            print("\n--- All Registered Students ---")
            res = list_all_students()
            if res["success"]:
                format_student_table(res["data"])
            else:
                print_error(res["error"])

        elif choice == "6":
            print("\n--- Class Performance Summary ---")
            res = get_all_results_summary()
            if res["success"] and res["data"]:
                header = f"{'Roll No':<12} | {'Name':<20} | {'Total':<10} | {'%':<6} | {'Grade':<5} | {'Status'}"
                print("-" * len(header))
                print(header)
                print("-" * len(header))
                passed = 0
                for r in res["data"]:
                    tot = f"{r['total_obtained']:.0f}/{r['total_max']:.0f}"
                    status_lbl = "PASS" if r["status"] == "PASS" else ("FAIL" if r["status"] == "FAIL" else r["status"])
                    if r["status"] == "PASS":
                        passed += 1
                    print(f"{r['roll_no']:<12} | {r['name']:<20} | {tot:<10} | {r['percentage']:<6.1f} | {r['grade']:<5} | {status_lbl}")
                print("-" * len(header))
                pass_pct = (passed / len(res["data"])) * 100 if res["data"] else 0
                print(f"Total Evaluated: {len(res['data'])}, Passed: {passed}, Failed: {len(res['data']) - passed}, Pass Rate: {pass_pct:.1f}%")
            else:
                print("No result records to summarize.")

        elif choice == "7":
            print("\n--- Delete Subject Marks ---")
            roll_no = input("Student Roll Number: ").strip()
            subj = input("Subject Name: ").strip()
            res = delete_subject_marks(roll_no, subj)
            if res["success"]:
                print_success(res["message"])
            else:
                print_error(res["error"])

        elif choice == "8":
            print("\n--- Delete Student Record ---")
            roll_no = input("Student Roll Number: ").strip()
            confirm = input(f"Are you sure you want to permanently delete {roll_no}? (y/N): ").strip().lower()
            if confirm == "y":
                res = delete_student(roll_no)
                if res["success"]:
                    print_success(res["message"])
                else:
                    print_error(res["error"])
            else:
                print_info("Deletion cancelled.")

        elif choice == "9":
            seed_sample_data()

        elif choice == "0":
            print("\nExiting Student Result Management System. Goodbye!")
            break
        else:
            print_error("Invalid choice. Please enter a number from 0 to 9.")


# ============================================================================
# Serverless / AWS Lambda Handlers
# ============================================================================

def build_lambda_response(status_code, body):
    """Construct an AWS API Gateway compatible JSON response."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(body)
    }


def lambda_handler(event, context=None):
    """
    Main AWS Lambda routing handler.
    Inspects event HTTP method and path to route to sub-functions.
    """
    init_db()
    http_method = event.get("httpMethod", "GET").upper()
    path = event.get("path", "")
    query_params = event.get("queryStringParameters") or {}
    body_raw = event.get("body")
    body = {}
    if body_raw:
        try:
            body = json.loads(body_raw) if isinstance(body_raw, str) else body_raw
        except Exception:
            return build_lambda_response(400, {"error": "Invalid JSON body."})

    # Route: /students
    if path == "/students":
        if http_method == "GET":
            if "search" in query_params:
                res = search_students(query_params["search"])
            else:
                res = list_all_students()
            return build_lambda_response(200, res)
        elif http_method == "POST":
            res = register_student(
                roll_no=body.get("roll_no"),
                name=body.get("name"),
                email=body.get("email"),
                course=body.get("course"),
                semester=body.get("semester")
            )
            code = 201 if res["success"] else 400
            return build_lambda_response(code, res)

    # Route: /students/{roll_no}
    if path.startswith("/students/") and "/results" not in path:
        roll_no = path.split("/")[2]
        if http_method == "GET":
            res = get_student_by_roll_no(roll_no)
            code = 200 if res["success"] else 404
            return build_lambda_response(code, res)
        elif http_method == "PUT":
            res = update_student(
                roll_no=roll_no,
                name=body.get("name"),
                email=body.get("email"),
                course=body.get("course"),
                semester=body.get("semester")
            )
            code = 200 if res["success"] else 400
            return build_lambda_response(code, res)
        elif http_method == "DELETE":
            res = delete_student(roll_no)
            code = 200 if res["success"] else 404
            return build_lambda_response(code, res)

    # Route: /students/{roll_no}/results
    if path.startswith("/students/") and path.endswith("/results"):
        roll_no = path.split("/")[2]
        if http_method == "GET":
            res = get_student_result(roll_no)
            code = 200 if res["success"] else 404
            return build_lambda_response(code, res)
        elif http_method == "POST":
            res = add_or_update_subject_marks(
                roll_no=roll_no,
                subject_name=body.get("subject_name"),
                marks_obtained=body.get("marks_obtained"),
                max_marks=body.get("max_marks", 100.0)
            )
            code = 200 if res["success"] else 400
            return build_lambda_response(code, res)

    # Route: /results/summary
    if path == "/results/summary" and http_method == "GET":
        res = get_all_results_summary()
        return build_lambda_response(200, res)

    return build_lambda_response(404, {"error": f"Endpoint not found: {http_method} {path}"})


# ============================================================================
# Direct Command-Line Arguments Handler
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Serverless Student Result Management System CLI",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--interactive", action="store_true", help="Launch interactive CLI menu")
    parser.add_argument("--serve", "--web", dest="serve_web", action="store_true", help="Run interactive Web Dashboard on localhost")
    parser.add_argument("--port", type=int, default=None, help="Port for web dashboard (default 5050)")
    parser.add_argument("--seed", action="store_true", help="Seed database with sample dataset")
    parser.add_argument("--init-db", action="store_true", help="Initialize database tables")
    parser.add_argument("--reset-db", action="store_true", help="Reset all tables in database")

    # Student operations
    parser.add_argument("--register-student", action="store_true", help="Register a student")
    parser.add_argument("--roll", type=str, help="Student Roll Number")
    parser.add_argument("--name", type=str, help="Student Full Name")
    parser.add_argument("--email", type=str, help="Student Email")
    parser.add_argument("--course", type=str, help="Course Name")
    parser.add_argument("--sem", type=int, help="Semester")

    # Result operations
    parser.add_argument("--add-marks", action="store_true", help="Add or update subject marks")
    parser.add_argument("--subject", type=str, help="Subject Name")
    parser.add_argument("--marks", type=float, help="Marks Obtained")
    parser.add_argument("--max", type=float, default=100.0, help="Maximum Marks (default 100)")

    # View & Search operations
    parser.add_argument("--view-result", type=str, metavar="ROLL_NO", help="Display full result card for a student")
    parser.add_argument("--list-students", action="store_true", help="List all registered students")
    parser.add_argument("--view-all", action="store_true", help="Display class performance summary table")
    parser.add_argument("--search", type=str, metavar="QUERY", help="Search student by roll no or name")
    parser.add_argument("--delete-student", type=str, metavar="ROLL_NO", help="Delete a student record")

    args = parser.parse_args()

    # If no arguments provided, launch interactive menu
    if len(sys.argv) == 1 or args.interactive:
        interactive_cli()
        return

    if args.serve_web:
        from src.server import run_server
        run_server(port=args.port)
        return

    if args.init_db:
        init_db()
        print_success(f"Database initialized at {get_db_path()}")

    elif args.reset_db:
        reset_db()
        print_success("Database reset successfully.")

    elif args.seed:
        seed_sample_data()

    elif args.register_student:
        if not (args.roll and args.name and args.email and args.course and args.sem):
            print_error("Missing required arguments for registration: --roll, --name, --email, --course, --sem")
            sys.exit(1)
        res = register_student(args.roll, args.name, args.email, args.course, args.sem)
        if res["success"]:
            print_success(res["message"])
        else:
            print_error(res["error"])

    elif args.add_marks:
        if not (args.roll and args.subject and args.marks is not None):
            print_error("Missing required arguments for adding marks: --roll, --subject, --marks")
            sys.exit(1)
        res = add_or_update_subject_marks(args.roll, args.subject, args.marks, args.max)
        if res["success"]:
            print_success(res["message"])
        else:
            print_error(res["error"])

    elif args.view_result:
        res = get_student_result(args.view_result)
        if res["success"]:
            print_result_card(res["data"])
        else:
            print_error(res["error"])

    elif args.list_students:
        res = list_all_students()
        if res["success"]:
            format_student_table(res["data"])
        else:
            print_error(res["error"])

    elif args.view_all:
        res = get_all_results_summary()
        if res["success"] and res["data"]:
            header = f"{'Roll No':<12} | {'Name':<20} | {'Total':<10} | {'%':<6} | {'Grade':<5} | {'Status'}"
            print("-" * len(header))
            print(header)
            print("-" * len(header))
            for r in res["data"]:
                tot = f"{r['total_obtained']:.0f}/{r['total_max']:.0f}"
                print(f"{r['roll_no']:<12} | {r['name']:<20} | {tot:<10} | {r['percentage']:<6.1f} | {r['grade']:<5} | {r['status']}")
            print("-" * len(header))
        else:
            print("No records found.")

    elif args.search:
        res = search_students(args.search)
        if res["success"]:
            format_student_table(res["data"])
        else:
            print_error(res["error"])

    elif args.delete_student:
        res = delete_student(args.delete_student)
        if res["success"]:
            print_success(res["message"])
        else:
            print_error(res["error"])


if __name__ == "__main__":
    main()
