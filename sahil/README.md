# Serverless Student Result Management System

A modular, high-performance, and serverless-ready Student Result Management System implemented in Python. The system provides automated student registration, subject marks recording, automatic calculation of total marks, percentage, letter grades, and pass/fail statuses, alongside both an interactive CLI and AWS Lambda serverless function handlers.

---

## 1. Overview of the Project
The **Serverless Student Result Management System** is built to modernize academic record tracking and result calculation. Designed with a dual-execution paradigm, it enables administrators, teachers, and students to interact through an intuitive command-line interface (CLI) locally, while featuring a clean microservice architecture ready for deployment as cloud functions on AWS Lambda via the Serverless Framework.

### System Architecture Flow
```
                     +---------------------------------------+
                     |                 User                  |
                     +---------------------------------------+
                                         |
                                         v
                     +---------------------------------------+
                     |            CLI Application            |
                     |             (src/app.py)              |
                     +---------------------------------------+
                                         |
                                         v
                     +---------------------------------------+
                     |            API / Functions            |
                     |           (Serverless Layer)          |
                     +---------------------------------------+
                                    /         \
                                   /           \
                                  v             v
       +----------------------------+         +----------------------------+
       |      Student Function      | <=====> |      Result Function       |
       |     (src/students.py)      |         |      (src/results.py)      |
       +----------------------------+         +----------------------------+
                                  \             /
                                   \           /
                                    v         v
                     +---------------------------------------+
                     |         Database Persistence          |
                     |  SQLite (Local) / AWS DynamoDB (Cloud)|
                     +---------------------------------------+
                                         |
                                         v
                     +---------------------------------------+
                     |         Student Result Card           |
                     |      (Grade, Status, Summary)         |
                     +---------------------------------------+
```

---

## 2. Key Features
- **Student Registration & Lifecycle:** Register students with unique roll numbers, names, email validation, course information, and semester levels.
- **Subject Marks Entry & Updates:** Add and update marks with boundary validation ($0 \le marks \le max\_marks$) and idempotent upsert support.
- **Automated Academic Computation Engine:**
  - Total marks obtained and total maximum marks.
  - Overall percentage calculation rounded to two decimals.
  - Letter grade assignment ($A+, A, B+, B, C, P, F$).
  - Pass/Fail status calculation with dual verification (individual subject threshold and cumulative pass percentage).
- **Search & Filter:** Search student records instantly by roll number, name keyword, or email.
- **Interactive Terminal UI & Scriptable CLI:** Menu-driven terminal UI with tabular views alongside command-line argument flags for automated pipelines.
- **Serverless Cloud Ready:** Native AWS Lambda handlers and `serverless.yml` configuration.
- **Automated Test Suite:** Complete unit tests covering business logic, calculations, database constraints, and API events.
- **Formal Academic Report Generation:** Automated generator creating formatted PDF and DOCX reports in `docs/`.

---

## 3. Technologies & Tools Used
- **Programming Language:** Python 3.10+ (Tested on Python 3.14)
- **Local Storage / Relational Database:** SQLite3 with foreign keys and index optimizations
- **Cloud Infrastructure:** Serverless Framework v3 / AWS Lambda / Amazon API Gateway
- **Document & PDF Generation:** `reportlab`, `python-docx`
- **Testing Framework:** Python standard library `unittest`
- **Configuration & Data Formats:** JSON, YAML, SQL

---

## 4. Steps to Install & Run the Project

### Step 4.1: Verify Python Version
Before starting, ensure that Python is installed on your system. Run:
```bash
python --version
```
*Expected Output: `Python 3.10.x` or higher (e.g., `Python 3.14.7`)*.

### Step 4.2: Clone or Navigate to the Repository
```bash
cd sahil
```

### Step 4.3: (Optional) Set Up Virtual Environment
```bash
python -m venv venv

# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# On macOS/Linux:
source venv/bin/activate
```

### Step 4.4: Install Required Packages
```bash
pip install -r requirements.txt
```

### Step 4.5: Initialize and Seed the Database
Initialize the database and populate it with sample student records:
```bash
python src/app.py --seed
```

### Step 4.6: Run the Interactive CLI Application
Launch the interactive menu:
```bash
python src/app.py
```
Or explicitly:
```bash
python src/app.py --interactive
```

### Step 4.7: CLI Command-Line Direct Execution Examples
You can also execute single commands directly via command-line arguments:

- **Register a Student:**
  ```bash
  python src/app.py --register-student --roll CS2026100 --name "Aditi Rao" --email "aditi@example.com" --course "B.Tech CS" --sem 4
  ```

- **Add / Update Subject Marks:**
  ```bash
  python src/app.py --add-marks --roll CS2026100 --subject "Cloud Computing" --marks 88 --max 100
  ```

- **View Student Result Card:**
  ```bash
  python src/app.py --view-result CS2026100
  ```

- **View All Students Class Performance Summary:**
  ```bash
  python src/app.py --view-all
  ```

- **Search Students:**
  ```bash
  python src/app.py --search "Aditi"
  ```

- **List All Registered Students:**
  ```bash
  python src/app.py --list-students
  ```

- **Generate Academic Project Report (PDF & Word):**
  ```bash
  python docs/generate_report.py
  ```

---

## 5. Instructions for Testing

The project includes an automated test suite verifying edge cases, validations, calculations, and lambda handlers.

Run all automated unit tests using Python's test discovery:
```bash
python -m unittest discover -s tests -v
```

### Example Test Execution Output:
```text
test_add_subject_marks (test_app.TestStudentResultManagementSystem.test_add_subject_marks) ... ok
test_comprehensive_result_calculation (test_app.TestStudentResultManagementSystem.test_comprehensive_result_calculation) ... ok
test_delete_student_cascade (test_app.TestStudentResultManagementSystem.test_delete_student_cascade) ... ok
test_delete_subject_marks (test_app.TestStudentResultManagementSystem.test_delete_subject_marks) ... ok
test_duplicate_roll_number_rejection (test_app.TestStudentResultManagementSystem.test_duplicate_roll_number_rejection) ... ok
test_grade_and_status_computation (test_app.TestStudentResultManagementSystem.test_grade_and_status_computation) ... ok
test_invalid_email_validation (test_app.TestStudentResultManagementSystem.test_invalid_email_validation) ... ok
test_invalid_semester_validation (test_app.TestStudentResultManagementSystem.test_invalid_semester_validation) ... ok
test_lambda_handler_post_and_get_student (test_app.TestStudentResultManagementSystem.test_lambda_handler_post_and_get_student) ... ok
test_marks_out_of_range (test_app.TestStudentResultManagementSystem.test_marks_out_of_range) ... ok
test_register_student_success (test_app.TestStudentResultManagementSystem.test_register_student_success) ... ok
test_search_students (test_app.TestStudentResultManagementSystem.test_search_students) ... ok
test_update_existing_subject_marks (test_app.TestStudentResultManagementSystem.test_update_existing_subject_marks) ... ok
test_update_student_details (test_app.TestStudentResultManagementSystem.test_update_student_details) ... ok

----------------------------------------------------------------------
Ran 14 tests in 0.377s

OK
```

---

## 6. Screenshots & Terminal Previews

### 6.1 Interactive Main Menu
```text
============================================================
       SERVERLESS STUDENT RESULT MANAGEMENT SYSTEM          
============================================================
  1. Register New Student
  2. Add / Update Subject Marks
  3. View Individual Student Result Card
  4. Search Students (by Roll No, Name, or Email)
  5. List All Registered Students
  6. View Class Performance Summary
  7. Delete a Subject Result
  8. Delete a Student Record
  9. Seed Sample Records (sample/sample_data.json)
  0. Exit
------------------------------------------------------------
Select an option (0-9):
```

### 6.2 Student Result Card (Detailed Report)
```text
====================================================================
                  STUDENT RESULT CARD - CS2026001                   
====================================================================
 Student Name : Aarav Sharma              Roll Number : CS2026001
 Course       : B.Tech Computer Science   Semester    : 4
 Email        : aarav.sharma@example.com
--------------------------------------------------------------------
 #   | Subject Name                   | Marks   | Max   | %      | Status
--------------------------------------------------------------------
 1   | Computer Networks              | 79.0    | 100.0 | 79.0   | [PASS]
 2   | Data Structures & Algorithms   | 88.0    | 100.0 | 88.0   | [PASS]
 3   | Database Management Systems    | 92.0    | 100.0 | 92.0   | [PASS]
 4   | Operating Systems              | 85.0    | 100.0 | 85.0   | [PASS]
 5   | Software Engineering           | 91.0    | 100.0 | 91.0   | [PASS]
====================================================================
 Total Obtained : 435.0 / 500.0
 Percentage     : 87.00%
 Grade          : A
 Final Status   : PASS
====================================================================
```

### 6.3 Class Performance Summary Table
```text
--------------------------------------------------------------------------
Roll No      | Name                 | Total      | %      | Grade | Status
--------------------------------------------------------------------------
CS2026001    | Aarav Sharma         | 435/500    | 87.0   | A     | PASS
CS2026002    | Ananya Patel         | 471/500    | 94.2   | A+    | PASS
CS2026003    | Rohan Verma          | 300/500    | 60.0   | B     | PASS
CS2026004    | Diya Sengupta        | 366/500    | 73.2   | B+    | PASS
CS2026005    | Kabir Mehta          | 206/500    | 41.2   | F     | FAIL
--------------------------------------------------------------------------
```

---

## 7. Project Structure
```text
Serverless Student-Result-Management System/
├── src/
│   ├── app.py              # CLI Application, Argument Parser & Serverless Handlers
│   ├── database.py         # SQLite connection, Schema creation, Indexing & Transactions
│   ├── students.py         # Student registration, profile updates, search & validation
│   └── results.py          # Subject marks, Total, Percentage, Grade & Pass/Fail logic
├── tests/
│   └── test_app.py         # Comprehensive automated unit tests
├── data/
│   └── results.db          # SQLite persistent database file
├── config/
│   └── config.example.json # Application configuration and grading thresholds
├── sample/
│   └── sample_data.json    # Sample student records for demonstration and seeding
├── docs/
│   ├── PROJECT_REPORT.md   # Comprehensive 15-section project report (Markdown)
│   ├── project-report.docx # Formal Microsoft Word report document
│   ├── project-report.pdf  # Portal submission PDF report
│   └── generate_report.py  # Automated report generator script
├── requirements.txt        # Project dependencies
├── serverless.yml          # Serverless Framework AWS Lambda & API Gateway config
├── statement.md            # Problem statement, scope, target users & features
├── .gitignore              # Git ignore rules for clean repository tracking
└── README.md               # Main project documentation and setup guide
```
