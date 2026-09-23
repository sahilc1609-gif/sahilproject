# Problem Statement & Project Scope

## Project Title
**Serverless Student Result Management System**

---

## 1. Problem Statement
In traditional educational institutions and academic departments, managing student marks, semester grades, and academic reports is often handled manually using spreadsheets or monolithic, slow-loading legacy desktop databases. This approach suffers from several key shortcomings:
- **Data Inconsistency and Human Error:** Manual calculations of total marks, percentages, grades, and pass/fail statuses often lead to calculation errors and grading discrepancies.
- **Scalability Bottlenecks:** Monolithic web applications require continuous server provisioning, resulting in idle compute costs during vacation periods and performance degradation during peak exam result release days.
- **Lack of Rapid Access:** Faculty members and academic coordinators struggle to quickly query, filter, and inspect individual student report cards or generate semester performance overviews.
- **Complex Deployment & Maintenance:** On-premise student management suites demand heavy database setups, difficult backups, and complex installations.

To resolve these challenges, there is a distinct need for a **lightweight, modular, serverless-ready Student Result Management System** that supports both immediate command-line execution (for rapid local administrative tasks and batch automation) and cloud microservices (for zero-maintenance, highly scalable serverless deployment).

---

## 2. Scope of the Project
The **Serverless Student Result Management System** is engineered to provide an end-to-end result computation and academic record tracking solution.

### In Scope:
1. **Student Profile Lifecycle:**
   - Registration of students with unique roll numbers, full names, verified email addresses, academic courses, and semester levels.
   - Comprehensive input validation and data sanitization.
   - Profile updating and cascaded deletion of associated academic records upon student departure.
2. **Subject & Marks Management:**
   - Recording marks obtained alongside maximum attainable marks for individual subjects.
   - Idempotent upsert functionality (adding new subjects or updating existing marks seamlessly).
   - Subject-level deletion and validation ensuring marks do not exceed maximum bounds.
3. **Automated Academic Computation Engine:**
   - Accurate computation of total marks obtained and cumulative maximum marks.
   - Percentage calculation rounded to two decimal places.
   - Dynamic letter grade allocation based on institutional thresholds ($A+, A, B+, B, C, P, F$).
   - Comprehensive pass/fail evaluation incorporating both aggregate percentage criteria ($ \ge 40\% $) and individual subject clearance criteria ($ \ge 35\% $).
4. **Interactive CLI & Batch Automation:**
   - Menu-driven terminal interface for intuitive user interaction.
   - Scriptable CLI arguments for headless automation and testing pipelines.
   - Seeding utilities for demonstration and verification datasets.
5. **Serverless Cloud Architecture:**
   - Serverless configuration (`serverless.yml`) defining AWS Lambda functions triggered via Amazon API Gateway HTTP endpoints.
   - Dual-persistence abstraction: Local SQLite for rapid development and testing; AWS DynamoDB schema for cloud-native deployment.
6. **Academic Reporting & Documentation:**
   - Generation of printable student result cards and class summary tables.
   - Complete project documentation, unit testing suite, and formal project report in PDF and DOCX formats.

### Out of Scope:
- Online fee payment gateway integration.
- Biometric attendance tracking.
- Multi-tenant enterprise single-sign-on (SSO) with Active Directory (planned as future enhancement).

---

## 3. Target Users
The system is designed to serve multiple stakeholder personas across educational and administrative workflows:
- **Academic Coordinators & Faculty Members:**
  Quickly enter subject marks, modify student scores, track semester performance, and identify at-risk students who have failed specific subjects.
- **Department Heads & Examination Officers:**
  Generate consolidated class reports, assess overall semester pass percentages, examine grade distributions, and audit academic integrity.
- **Students:**
  Query and view itemized report cards containing subject-wise scores, percentage, letter grade, and overall pass/fail status.
- **System Administrators & DevOps Engineers:**
  Deploy, monitor, and scale the application at minimal operational cost using serverless infrastructure without managing dedicated virtual machines.

---

## 4. High-Level Features
- **Student Registration & Directory:** Validated storage of academic profiles with roll-number uniqueness guarantees.
- **Subject Marks Entry & Updates:** Flexible recording of scores with range enforcement and real-time validation.
- **Automated Grade & Status Engine:** Instant calculation of cumulative marks, percentages, letter grades, and multi-criteria pass/fail determination.
- **Detailed Report Card Generator:** ASCII/formatted terminal report cards ready for inspection and export.
- **Search & Filter Capability:** Instant search across roll numbers, student names, and emails.
- **Dual Execution Modes:** Fully interactive terminal menu and non-interactive scripted command-line flags.
- **Cloud-Ready Serverless Architecture:** Built-in AWS Lambda handlers and API Gateway routing configurations.
- **Automated Testing Suite:** 100% test coverage over business logic, database transactions, and cloud event dispatchers.
