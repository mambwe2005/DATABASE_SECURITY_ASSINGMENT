"""Shared helpers for the BIT3360 Database Security prototype.

Contains: connection helper, salted password hashing (PBKDF2) and a secure
login function that uses a parameterised query.
"""
import hashlib
import hmac
import os
import secrets

import pymysql

DB_NAME = "zuct_records"
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = int(os.environ.get("DB_PORT", "3306"))

# DEMO credentials for the throw-away demo database (see sql/03_...).
# In a real application these come from environment variables / a vault.
DB_ACCOUNTS = {
    "db_admin": "Admin#Demo2026",
    "registrar_user": "Registrar#Demo2026",
    "lecturer_user": "Lecturer#Demo2026",
    "auditor_user": "Auditor#Demo2026",
    "app_service": "AppSvc#Demo2026",
}

# PBKDF2-HMAC-SHA256 work factor (OWASP Password Storage Cheat Sheet value).
PBKDF2_ITERATIONS = 600_000


def connect(account, autocommit=False):
    """Open a connection as one of the demo database accounts."""
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=account,
        password=DB_ACCOUNTS[account],
        database=DB_NAME,
        autocommit=autocommit,
    )


# ----------------------------------------------------------------------
# Password hashing (authentication)
# ----------------------------------------------------------------------
def hash_password(password, salt=None, iterations=PBKDF2_ITERATIONS):
    """Return 'pbkdf2_sha256$iterations$salt_hex$hash_hex' (random salt)."""
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    return f"pbkdf2_sha256${iterations}${salt.hex()}${digest.hex()}"


def verify_password(password, stored):
    """Check a password against a stored hash in constant time."""
    try:
        _, iters, salt_hex, hash_hex = stored.split("$")
        candidate = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt_hex), int(iters)
        )
        return hmac.compare_digest(candidate.hex(), hash_hex)
    except (ValueError, AttributeError):
        return False


_DUMMY_HASH = hash_password("dummy-password-for-timing")


def login_secure(conn, username, password):
    """Authenticate an application user.

    * The username is passed as a PARAMETER (%s), never concatenated into SQL.
    * The password is checked against a salted PBKDF2 hash.
    * For unknown users we still run a hash comparison so the response time
      does not reveal whether the username exists.
    Returns the user's role on success, otherwise None.
    """
    with conn.cursor() as cur:
        cur.execute(
            "SELECT password_hash, role FROM app_users WHERE username = %s",
            (username,),
        )
        row = cur.fetchone()
    if row is None:
        verify_password(password, _DUMMY_HASH)
        return None
    stored_hash, role = row
    return role if verify_password(password, stored_hash) else None


# ----------------------------------------------------------------------
# Small output helpers
# ----------------------------------------------------------------------
def banner(title):
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def print_table(headers, rows, max_width=46):
    """Print rows as a simple text table (long cells are shortened)."""
    def cell(v):
        s = "NULL" if v is None else str(v)
        return s if len(s) <= max_width else s[: max_width - 3] + "..."

    data = [[cell(v) for v in r] for r in rows]
    widths = [len(h) for h in headers]
    for r in data:
        for i, v in enumerate(r):
            widths[i] = max(widths[i], len(v))
    line = "  ".join("-" * w for w in widths)
    print("  " + "  ".join(h.ljust(w) for h, w in zip(headers, widths)))
    print("  " + line)
    for r in data:
        print("  " + "  ".join(v.ljust(w) for v, w in zip(r, widths)))
    if not data:
        print("  (no rows)")


def short_error(exc):
    """Compact MariaDB error text: '(1142) DELETE command denied ...'."""
    code = exc.args[0] if exc.args else "?"
    msg = exc.args[1] if len(exc.args) > 1 else str(exc)
    return f"({code}) {msg}"
