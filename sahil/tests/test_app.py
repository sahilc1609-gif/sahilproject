"""
Comprehensive Automated Test Suite
Tests:
  - Database schema initialization
  - Student registration, validation, update, delete
  - Subject marks addition, updating, deletion
  - Calculations: total marks, percentage, letter grades, pass/fail status
  - Search operations
  - Serverless / AWS Lambda event routing
"""

import unittest
import os
import sys
import json
import tempfile
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database import init_db, get_connection
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
    add_multiple_subject_marks,
    delete_subject_marks,
    get_student_result,
    compute_grade_and_status,
    get_all_results_summary
)
from src.app import lambda_handler


class TestStudentResultManagementSystem(unittest.TestCase):
    def setUp(self):
        # Create an isolated temporary SQLite database for each test
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_results.db")
        init_db(self.db_path)

    def tearDown(self):
        # Clean up temporary database files
        self.temp_dir.cleanup()

    # ------------------------------------------------------------------------
    # 1. Student Registration & Validation Tests
    # ------------------------------------------------------------------------
    def test_register_student_success(self):
        res = register_student("CS101", "Alice Smith", "alice@example.com", "Computer Science", 3, self.db_path)
        self.assertTrue(res["success"])
        self.assertEqual(res["data"]["roll_no"], "CS101")
        self.assertEqual(res["data"]["name"], "Alice Smith")

    def test_duplicate_roll_number_rejection(self):
        register_student("CS101", "Alice Smith", "alice@example.com", "Computer Science", 3, self.db_path)
        dup_res = register_student("CS101", "Bob White", "bob@example.com", "Computer Science", 3, self.db_path)
        self.assertFalse(dup_res["success"])
        self.assertIn("already exists", dup_res["error"])

    def test_invalid_email_validation(self):
        res = register_student("CS102", "Charlie", "invalid-email-string", "Computer Science", 3, self.db_path)
        self.assertFalse(res["success"])
        self.assertIn("Invalid email format", res["error"])

    def test_invalid_semester_validation(self):
        res = register_student("CS103", "David", "david@example.com", "Computer Science", 15, self.db_path)
        self.assertFalse(res["success"])
        self.assertIn("Semester must be an integer between 1 and 12", res["error"])

    def test_update_student_details(self):
        register_student("CS104", "Emma Watson", "emma@example.com", "IT", 2, self.db_path)
        up_res = update_student("CS104", name="Emma Watson-Brown", semester=3, db_path=self.db_path)
        self.assertTrue(up_res["success"])

        fetched = get_student_by_roll_no("CS104", self.db_path)
        self.assertEqual(fetched["data"]["name"], "Emma Watson-Brown")
        self.assertEqual(fetched["data"]["semester"], 3)

    def test_delete_student_cascade(self):
        register_student("CS105", "Frank Miller", "frank@example.com", "ECE", 1, self.db_path)
        add_or_update_subject_marks("CS105", "Physics", 85, 100, self.db_path)

        del_res = delete_student("CS105", self.db_path)
        self.assertTrue(del_res["success"])

        # Check student no longer exists
        fetched = get_student_by_roll_no("CS105", self.db_path)
        self.assertFalse(fetched["success"])

        # Verify associated marks were cascaded
        conn = get_connection(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as cnt FROM results")
        count = cur.fetchone()["cnt"]
        conn.close()
        self.assertEqual(count, 0)

    # ------------------------------------------------------------------------
    # 2. Results & Marks Operations Tests
    # ------------------------------------------------------------------------
    def test_add_subject_marks(self):
        register_student("CS201", "Grace Hopper", "grace@example.com", "CS", 4, self.db_path)
        res = add_or_update_subject_marks("CS201", "Compilers", 92.5, 100, self.db_path)
        self.assertTrue(res["success"])
        self.assertEqual(res["data"]["marks_obtained"], 92.5)

    def test_update_existing_subject_marks(self):
        register_student("CS202", "Alan Turing", "alan@example.com", "CS", 4, self.db_path)
        add_or_update_subject_marks("CS202", "Algorithms", 88, 100, self.db_path)
        # Update marks for the same subject
        up_res = add_or_update_subject_marks("CS202", "Algorithms", 96, 100, self.db_path)
        self.assertTrue(up_res["success"])

        card = get_student_result("CS202", self.db_path)
        self.assertEqual(len(card["data"]["subjects"]), 1)
        self.assertEqual(card["data"]["subjects"][0]["marks_obtained"], 96.0)

    def test_marks_out_of_range(self):
        register_student("CS203", "John von Neumann", "john@example.com", "Math", 2, self.db_path)
        # Marks exceeds max marks
        res = add_or_update_subject_marks("CS203", "Calculus", 110, 100, self.db_path)
        self.assertFalse(res["success"])
        self.assertIn("must be between 0 and 100", res["error"])

        # Negative marks
        res2 = add_or_update_subject_marks("CS203", "Calculus", -5, 100, self.db_path)
        self.assertFalse(res2["success"])

    def test_delete_subject_marks(self):
        register_student("CS204", "Ken Thompson", "ken@example.com", "CS", 3, self.db_path)
        add_or_update_subject_marks("CS204", "Unix Architecture", 89, 100, self.db_path)

        del_res = delete_subject_marks("CS204", "Unix Architecture", self.db_path)
        self.assertTrue(del_res["success"])

        card = get_student_result("CS204", self.db_path)
        self.assertEqual(len(card["data"]["subjects"]), 0)

    def test_add_multiple_subject_marks(self):
        register_student("CS205", "Grace Hopper", "grace@example.com", "CS", 4, self.db_path)
        subjects = [
            {"subject_name": "Compilers", "marks_obtained": 95, "max_marks": 100},
            {"subject_name": "COBOL", "marks_obtained": 92, "max_marks": 100},
            {"subject_name": "Algorithms", "marks_obtained": 88, "max_marks": 100}
        ]
        res = add_multiple_subject_marks("CS205", subjects, self.db_path)
        self.assertTrue(res["success"])
        self.assertEqual(res["saved_count"], 3)

        card = get_student_result("CS205", self.db_path)
        self.assertEqual(len(card["data"]["subjects"]), 3)
        self.assertEqual(card["data"]["summary"]["total_marks_obtained"], 275.0)
        self.assertEqual(card["data"]["summary"]["grade"], "A+")
        self.assertEqual(card["data"]["summary"]["status"], "PASS")

    # ------------------------------------------------------------------------
    # 3. Calculation Logic Tests (Total, Percentage, Grade, Pass/Fail)
    # ------------------------------------------------------------------------
    def test_grade_and_status_computation(self):
        # Grade A+ (>= 90%)
        g, s = compute_grade_and_status(92.5, 0)
        self.assertEqual(g, "A+")
        self.assertEqual(s, "PASS")

        # Grade A (>= 80%)
        g, s = compute_grade_and_status(84.0, 0)
        self.assertEqual(g, "A")
        self.assertEqual(s, "PASS")

        # Grade B+ (>= 70%)
        g, s = compute_grade_and_status(75.5, 0)
        self.assertEqual(g, "B+")
        self.assertEqual(s, "PASS")

        # Grade B (>= 60%)
        g, s = compute_grade_and_status(63.2, 0)
        self.assertEqual(g, "B")
        self.assertEqual(s, "PASS")

        # Grade C (>= 50%)
        g, s = compute_grade_and_status(54.0, 0)
        self.assertEqual(g, "C")
        self.assertEqual(s, "PASS")

        # Grade P (>= 40%)
        g, s = compute_grade_and_status(42.0, 0)
        self.assertEqual(g, "P")
        self.assertEqual(s, "PASS")

        # Grade F (< 40%)
        g, s = compute_grade_and_status(38.0, 0)
        self.assertEqual(g, "F")
        self.assertEqual(s, "FAIL")

        # If any subject failed, overall must be FAIL
        g, s = compute_grade_and_status(85.0, 1)
        self.assertEqual(g, "F")
        self.assertEqual(s, "FAIL")

    def test_comprehensive_result_calculation(self):
        register_student("CS301", "Ada Lovelace", "ada@example.com", "CS", 1, self.db_path)
        add_or_update_subject_marks("CS301", "Maths", 90, 100, self.db_path)
        add_or_update_subject_marks("CS301", "Logic", 95, 100, self.db_path)
        add_or_update_subject_marks("CS301", "Algorithms", 85, 100, self.db_path)

        res = get_student_result("CS301", self.db_path)
        self.assertTrue(res["success"])
        summary = res["data"]["summary"]
        self.assertEqual(summary["total_marks_obtained"], 270.0)
        self.assertEqual(summary["total_max_marks"], 300.0)
        self.assertEqual(summary["percentage"], 90.0)
        self.assertEqual(summary["grade"], "A+")
        self.assertEqual(summary["status"], "PASS")

    # ------------------------------------------------------------------------
    # 4. Search & Listing Tests
    # ------------------------------------------------------------------------
    def test_search_students(self):
        register_student("CS401", "Nikola Tesla", "nikola@example.com", "EE", 2, self.db_path)
        register_student("CS402", "Thomas Edison", "thomas@example.com", "EE", 2, self.db_path)

        res = search_students("Tesla", self.db_path)
        self.assertEqual(res["count"], 1)
        self.assertEqual(res["data"][0]["roll_no"], "CS401")

        res2 = search_students("CS40", self.db_path)
        self.assertEqual(res2["count"], 2)

    # ------------------------------------------------------------------------
    # 5. Serverless Lambda Event Handler Tests
    # ------------------------------------------------------------------------
    def test_lambda_handler_post_and_get_student(self):
        # Override environment DB path for lambda handler
        os.environ["RESULTS_DB_PATH"] = self.db_path

        # Test POST /students
        post_event = {
            "httpMethod": "POST",
            "path": "/students",
            "body": json.dumps({
                "roll_no": "LAMBDA01",
                "name": "Cloud Developer",
                "email": "cloud@example.com",
                "course": "Cloud Computing",
                "semester": 1
            })
        }
        resp = lambda_handler(post_event)
        self.assertEqual(resp["statusCode"], 201)

        # Test GET /students/LAMBDA01
        get_event = {
            "httpMethod": "GET",
            "path": "/students/LAMBDA01"
        }
        resp_get = lambda_handler(get_event)
        self.assertEqual(resp_get["statusCode"], 200)
        body = json.loads(resp_get["body"])
        self.assertEqual(body["data"]["name"], "Cloud Developer")

        # Test POST marks via Lambda
        marks_event = {
            "httpMethod": "POST",
            "path": "/students/LAMBDA01/results",
            "body": json.dumps({
                "subject_name": "Serverless Architecture",
                "marks_obtained": 94,
                "max_marks": 100
            })
        }
        resp_marks = lambda_handler(marks_event)
        self.assertEqual(resp_marks["statusCode"], 200)

        # Test GET results via Lambda
        card_event = {
            "httpMethod": "GET",
            "path": "/students/LAMBDA01/results"
        }
        resp_card = lambda_handler(card_event)
        self.assertEqual(resp_card["statusCode"], 200)
        card_body = json.loads(resp_card["body"])
        self.assertEqual(card_body["data"]["summary"]["percentage"], 94.0)

    # ------------------------------------------------------------------------
    # 6. Database Health & REST API Route Tests
    # ------------------------------------------------------------------------
    def test_database_health_check(self):
        from src.database import check_db_health
        health = check_db_health(self.db_path)
        self.assertEqual(health["status"], "healthy")
        self.assertEqual(health["integrity"], "ok")
        self.assertIn("student_count", health)
        self.assertIn("result_count", health)

    def test_flask_rest_api_database_routes(self):
        os.environ["RESULTS_DB_PATH"] = self.db_path
        from src.server import app
        client = app.test_client()

        # 1. Register student via REST
        reg_res = client.post("/api/students", json={
            "roll_no": "REST001",
            "name": "Rest Student",
            "email": "rest@example.com",
            "course": "REST API Course",
            "semester": 2,
            "subjects": [
                {"subject_name": "REST Basics", "marks_obtained": 88, "max_marks": 100}
            ]
        })
        self.assertEqual(reg_res.status_code, 201)

        # 2. Get student details via GET /api/students/<roll_no>
        stu_res = client.get("/api/students/REST001")
        self.assertEqual(stu_res.status_code, 200)
        stu_data = stu_res.get_json()
        self.assertEqual(stu_data["data"]["name"], "Rest Student")

        # 3. Update student via PUT /api/students/<roll_no>
        put_res = client.put("/api/students/REST001", json={"name": "Rest Student Updated"})
        self.assertEqual(put_res.status_code, 200)

        # 4. Get student result card via GET /api/results/<roll_no>
        card_res = client.get("/api/results/REST001")
        self.assertEqual(card_res.status_code, 200)
        card_data = card_res.get_json()
        self.assertEqual(card_data["data"]["summary"]["percentage"], 88.0)

        # 5. Check database health endpoint GET /api/health
        health_res = client.get("/api/health")
        self.assertEqual(health_res.status_code, 200)
        self.assertEqual(health_res.get_json()["status"], "healthy")

        # 6. Delete student via DELETE /api/students/<roll_no>
        del_res = client.delete("/api/students/REST001")
        self.assertEqual(del_res.status_code, 200)


if __name__ == "__main__":
    unittest.main()

