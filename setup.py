"""One-command setup for the BIT3360 Database Security prototype.

1. Runs the four SQL scripts with the `mysql` command-line client (as root).
2. Creates the application logins with salted PBKDF2 password hashes.

Usage:
    python setup.py

Environment variables (optional):
    MYSQL_BIN   path to the mysql client           (default: mysql)
    MYSQL_ARGS  extra client args, e.g. "-u root -p"   (default: -u root)
"""
import os
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "app"))

from common import connect, hash_password  # noqa: E402

SQL_FILES = [
    "01_schema.sql",
    "02_sample_data.sql",
    "03_users_and_privileges.sql",
    "04_audit_triggers.sql",
]

# Demo application logins: username, password, role
APP_USERS = [
    ("registrar1", "Registrar@123", "registrar"),
    ("lecturer1", "Lecturer@123", "lecturer"),
    ("auditor1", "Auditor@123", "auditor"),
]


def run_sql_scripts():
    mysql_bin = os.environ.get("MYSQL_BIN", "mysql")
    mysql_args = shlex.split(os.environ.get("MYSQL_ARGS", "-u root"))
    for name in SQL_FILES:
        path = ROOT / "sql" / name
        print(f"Running {name} ...")
        with open(path, "rb") as fh:
            result = subprocess.run(
                [mysql_bin, *mysql_args], stdin=fh, capture_output=True, text=True
            )
        if result.returncode != 0:
            print(result.stderr)
            sys.exit(f"Failed while running {name}")


def seed_app_users():
    print("Creating application logins (salted PBKDF2 hashes) ...")
    conn = connect("db_admin", autocommit=True)
    with conn.cursor() as cur:
        for username, password, role in APP_USERS:
            cur.execute(
                "INSERT INTO app_users (username, password_hash, role) VALUES (%s, %s, %s)",
                (username, hash_password(password), role),
            )
    conn.close()


if __name__ == "__main__":
    run_sql_scripts()
    seed_app_users()
    print("Setup complete. Run: python run_demos.py")
