"""Demo 4 - Authentication: salted password hashes and a safe login.

The application never stores passwords. It stores a salted PBKDF2 hash, and
the login query is parameterised.
"""
import sys

from common import banner, connect, hash_password, login_secure, print_table


def main():
    banner("DEMO 4 - AUTHENTICATION (hashed passwords + parameterised login)")

    conn = connect("app_service", autocommit=True)

    print("\nWhat is actually stored in the app_users table:")
    with conn.cursor() as cur:
        cur.execute("SELECT username, role, password_hash FROM app_users ORDER BY user_id")
        rows = cur.fetchall()
    print_table(["username", "role", "password_hash"], rows, max_width=60)
    print("  -> no plain-text passwords; the format is algorithm$iterations$salt$hash")

    print("\nSalting: hashing the SAME password twice gives different results:")
    h1, h2 = hash_password("Same@Password1"), hash_password("Same@Password1")
    print(f"  hash 1: {h1[:60]}...")
    print(f"  hash 2: {h2[:60]}...")
    print(f"  identical? {h1 == h2}  (so one cracked hash does not reveal other users)")

    print("\nLogin attempts:")
    cases = [
        ("registrar1", "Registrar@123", "correct username and password", "registrar"),
        ("registrar1", "wrong-password", "correct username, wrong password", None),
        ("nobody", "Registrar@123", "unknown username", None),
        ("' OR '1'='1' -- -", "anything", "SQL injection in the username field", None),
    ]
    failures = 0
    for username, password, label, expected in cases:
        role = login_secure(conn, username, password)
        outcome = f"logged in as {role}" if role else "REJECTED"
        ok = role == expected
        failures += 0 if ok else 1
        print(f"  {label:<40} -> {outcome}{'' if ok else '   <-- UNEXPECTED'}")

    conn.close()
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
