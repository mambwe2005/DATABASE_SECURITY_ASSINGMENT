"""Demo 1 - Access control: what each database user CAN and CANNOT do.

Every test runs as the named account inside a transaction that is rolled
back afterwards, so the demo can be repeated without changing the data.
"""
import sys

import pymysql

from common import banner, connect, short_error

# (account, description, SQL, expected_to_succeed)
TESTS = [
    # ---------------------------- db_admin ----------------------------
    ("db_admin", "Read all student columns", "SELECT * FROM students LIMIT 1", True),
    ("db_admin", "Read the audit log", "SELECT COUNT(*) FROM audit_log", True),
    # --------------------------- registrar_user -----------------------
    # DDL goes first: MariaDB commits the open transaction when a DDL statement
    # starts (even a denied one), which would make the later tests permanent.
    ("registrar_user", "Drop the grades table", "DROP TABLE grades", False),
    ("registrar_user", "Read phone / NRC / fees", "SELECT phone, nrc_number, fees_balance FROM students LIMIT 1", True),
    ("registrar_user", "Update a student's fees balance", "UPDATE students SET fees_balance = 0 WHERE student_id = 1", True),
    ("registrar_user", "Insert a new student",
     "INSERT INTO students (first_name,last_name,email,programme,year_of_study) VALUES ('Test','Student','test@student.example','BIT',1)", True),
    ("registrar_user", "Change a mark in grades", "UPDATE grades SET mark = 100 WHERE grade_id = 1", False),
    ("registrar_user", "Read app login hashes", "SELECT username, password_hash FROM app_users", False),
    ("registrar_user", "Read the audit log", "SELECT * FROM audit_log", False),
    ("registrar_user", "Delete from the audit log", "DELETE FROM audit_log", False),
    # --------------------------- lecturer_user ------------------------
    ("lecturer_user", "Read student names and programme", "SELECT first_name, last_name, programme FROM students", True),
    ("lecturer_user", "Update a mark", "UPDATE grades SET mark = 75 WHERE grade_id = 1", True),
    ("lecturer_user", "Insert a new mark",
     "INSERT INTO grades (student_id, course_code, mark, academic_year) VALUES (4, 'BIT3360', 66, '2025/2026')", True),
    ("lecturer_user", "Read student phone number", "SELECT phone FROM students", False),
    ("lecturer_user", "SELECT * on students (includes hidden columns)", "SELECT * FROM students", False),
    ("lecturer_user", "Delete a grade", "DELETE FROM grades WHERE grade_id = 1", False),
    ("lecturer_user", "Update a student's fees", "UPDATE students SET fees_balance = 0", False),
    ("lecturer_user", "Read the audit log", "SELECT * FROM audit_log", False),
    # ---------------------------- auditor_user ------------------------
    ("auditor_user", "Read the audit log", "SELECT COUNT(*) FROM audit_log", True),
    ("auditor_user", "Read student records", "SELECT * FROM students", False),
    ("auditor_user", "Read grades", "SELECT * FROM grades", False),
    ("auditor_user", "Modify the audit log", "UPDATE audit_log SET db_user = 'nobody'", False),
    ("auditor_user", "Delete from the audit log", "DELETE FROM audit_log", False),
    ("auditor_user", "Insert a fake audit entry",
     "INSERT INTO audit_log (table_name, action, record_id, db_user) VALUES ('students','DELETE',1,'x')", False),
]


def main():
    banner("DEMO 1 - ACCESS CONTROL (least privilege)")
    failures = 0
    current, conn = None, None
    for account, description, sql, expected in TESTS:
        if account != current:
            if conn:
                conn.rollback()
                conn.close()
            conn = connect(account)
            current = account
            print(f"\n--- Connected as {account} ---")
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
                cur.fetchall()
            allowed, detail = True, ""
        except pymysql.MySQLError as exc:
            allowed, detail = False, short_error(exc)
        ok = allowed == expected
        failures += 0 if ok else 1
        mark = "ALLOWED" if allowed else "DENIED "
        flag = "" if ok else "   <-- UNEXPECTED"
        print(f"  [{mark}] {description}{flag}")
        if detail:
            print(f"            {detail}")
    if conn:
        conn.rollback()
        conn.close()
    total = len(TESTS)
    print(f"\nResult: {total - failures}/{total} tests behaved as designed.")
    return failures


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
