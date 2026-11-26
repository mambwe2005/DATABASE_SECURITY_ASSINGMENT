"""Demo 2 - SQL injection vs parameterised queries (on our own demo database).

Scenario: a lecturer portal lets staff search BIT students by last name.
The portal connects as 'app_service', a low-privilege account.

  search_vulnerable()  builds the SQL by gluing user input into the string.
  search_secure()      sends the input as a parameter (%s).
"""
import sys

import pymysql

from common import banner, connect, print_table, short_error

HEADERS = ["id", "first_name", "last_name", "programme"]


# ---------------------------------------------------------------- BAD
def search_vulnerable(conn, last_name):
    """INSECURE: user input is concatenated into the SQL text."""
    sql = (
        "SELECT student_id, first_name, last_name, programme FROM students "
        f"WHERE last_name = '{last_name}' AND programme = 'BIT'"
    )
    print(f"  SQL sent to the server:\n    {sql}")
    with conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()


# --------------------------------------------------------------- GOOD
def search_secure(conn, last_name):
    """SECURE: the query text is fixed; the input travels as a parameter."""
    sql = (
        "SELECT student_id, first_name, last_name, programme FROM students "
        "WHERE last_name = %s AND programme = %s"
    )
    with conn.cursor() as cur:
        print(f"  SQL sent to the server:\n    {cur.mogrify(sql, (last_name, 'BIT'))}")
        cur.execute(sql, (last_name, "BIT"))
        return cur.fetchall()


def attempt(func, conn, label, payload):
    print(f"\n* {label}")
    print(f"  Input typed into the search box: {payload!r}")
    try:
        rows = func(conn, payload)
        print(f"  Rows returned: {len(rows)}")
        print_table(HEADERS, rows)
        return rows
    except pymysql.MySQLError as exc:
        print(f"  Query FAILED: {short_error(exc)}")
        return None


def main():
    conn = connect("app_service", autocommit=True)

    banner("DEMO 2A - NORMAL USE (both versions behave the same)")
    attempt(search_vulnerable, conn, "Vulnerable version, honest input", "Mulenga")
    attempt(search_secure, conn, "Secure version, honest input", "Mulenga")

    banner("DEMO 2B - ATTACK 1: bypass the programme filter (tautology)")
    payload1 = "x' OR '1'='1' -- -"
    rows = attempt(search_vulnerable, conn, "VULNERABLE version", payload1)
    leaked_programmes = {r[3] for r in rows or []}
    attempt(search_secure, conn, "SECURE version", payload1)

    banner("DEMO 2C - ATTACK 2: UNION query to read the app_users table")
    payload2 = "x' UNION SELECT user_id, username, role, password_hash FROM app_users -- -"
    attempt(search_vulnerable, conn, "VULNERABLE version", payload2)
    attempt(search_secure, conn, "SECURE version", payload2)

    banner("DEMO 2D - ATTACK 3: try to read sensitive columns (NRC numbers)")
    print("  The vulnerable code is still injectable, but the app_service account")
    print("  has no privilege on nrc_number, so the database itself blocks it:")
    payload3 = "x' UNION SELECT student_id, nrc_number, phone, email FROM students -- -"
    attempt(search_vulnerable, conn, "VULNERABLE version", payload3)

    banner("DEMO 2E - ATTACK 4: stacked query to destroy data")
    payload4 = "x'; DROP TABLE students; -- -"
    attempt(search_vulnerable, conn, "VULNERABLE version", payload4)
    print("  (Blocked twice over: the driver refuses multiple statements and")
    print("   app_service has no DROP privilege.)")

    conn.close()
    print("\nSummary: parameterised queries stop injection at the source; least")
    print("privilege limits the damage if a mistake slips through.")
    # Sanity check used by run_demos.py: attack 1 must have leaked other programmes
    return 0 if leaked_programmes - {"BIT"} else 1


if __name__ == "__main__":
    sys.exit(main())
