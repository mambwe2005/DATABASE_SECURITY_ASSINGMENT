"""Demo 3 - Audit log: who changed what, and when.

Staff make some normal changes (as themselves), then the auditor reviews the
trail. Finally we show that staff cannot erase their tracks.
"""
import sys

import pymysql

from common import banner, connect, print_table, short_error


def run(account, sql, params=None):
    conn = connect(account, autocommit=True)
    with conn.cursor() as cur:
        cur.execute(sql, params)
    conn.close()


def try_tamper(account, description, sql):
    conn = connect(account, autocommit=True)
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        print(f"  [ALLOWED] {account}: {description}   <-- UNEXPECTED")
        ok = False
    except pymysql.MySQLError as exc:
        print(f"  [DENIED ] {account}: {description}")
        print(f"            {short_error(exc)}")
        ok = True
    conn.close()
    return ok


def main():
    banner("DEMO 3 - AUDIT LOG (triggers)")

    auditor = connect("auditor_user", autocommit=True)
    with auditor.cursor() as cur:
        cur.execute("SELECT COALESCE(MAX(log_id), 0) FROM audit_log")
        last_seen = cur.fetchone()[0]

    print("\nStep 1 - normal work by different staff members:")
    print("  registrar_user  : clears a student's fees balance")
    run("registrar_user", "UPDATE students SET fees_balance = 0 WHERE student_id = %s", (3,))
    print("  registrar_user  : registers a new student")
    run("registrar_user",
        "INSERT INTO students (first_name, last_name, email, programme, year_of_study) "
        "VALUES (%s, %s, %s, %s, %s)",
        ("Ngosa", "Kapambwe", "ngosa.kapambwe@student.example", "BIT", 1))
    print("  lecturer_user   : changes a mark from 48.00 to 62.00 (suspicious!)")
    run("lecturer_user", "UPDATE grades SET mark = 62 WHERE grade_id = 7")
    print("  lecturer_user   : enters a new mark")
    run("lecturer_user",
        "INSERT INTO grades (student_id, course_code, mark, academic_year) VALUES (%s,%s,%s,%s)",
        (4, "BIT3360", 59, "2025/2026"))
    print("  registrar_user  : removes the student they just registered")
    run("registrar_user", "DELETE FROM students WHERE email = %s", ("ngosa.kapambwe@student.example",))

    print("\nStep 2 - the auditor reviews the trail (new entries only):")
    with auditor.cursor() as cur:
        cur.execute(
            "SELECT log_id, DATE_FORMAT(changed_at, '%%H:%%i:%%S'), db_user, action, table_name, "
            "record_id, old_values, new_values FROM audit_log WHERE log_id > %s ORDER BY log_id",
            (last_seen,),
        )
        rows = cur.fetchall()
    print_table(["log", "time", "db_user", "action", "table", "rec"],
                [r[:6] for r in rows])

    print("\n  Detail of the changed mark (grades, UPDATE):")
    for r in rows:
        if r[4] == "grades" and r[3] == "UPDATE":
            print(f"    before: {r[6]}")
            print(f"    after : {r[7]}")
            print(f"    by    : {r[2]} at {r[1]}")

    print("\nStep 3 - can staff cover their tracks?")
    results = [
        try_tamper("registrar_user", "DELETE FROM audit_log", "DELETE FROM audit_log"),
        try_tamper("lecturer_user", "read the audit log", "SELECT * FROM audit_log"),
        try_tamper("auditor_user", "UPDATE audit_log (rewrite history)",
                   "UPDATE audit_log SET db_user = 'someone_else'"),
        try_tamper("auditor_user", "TRUNCATE audit_log", "TRUNCATE TABLE audit_log"),
    ]
    auditor.close()

    expected_entries = 5  # 2 registrar + 2 lecturer + 1 delete
    recorded_ok = len(rows) == expected_entries
    print(f"\nAudit entries recorded for the 5 changes: {len(rows)} "
          f"({'OK' if recorded_ok else 'UNEXPECTED'})")
    return 0 if (all(results) and recorded_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
