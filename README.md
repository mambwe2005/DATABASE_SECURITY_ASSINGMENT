# BIT3360 Advanced Databases - Database Security Prototype

Group assignment, Zambia University College of Technology.
Topic chosen: **Database Security**.

## The problem this prototype addresses

A university student-record database holds personal data (phone numbers, NRC
numbers, fee balances) and academic results. Different staff need different
access, applications must not be tricked into leaking data, and any change to
records must be traceable. The prototype shows four protections working together:

| Demo | Security measure | What it shows |
|------|------------------|---------------|
| 1 | Access control (least privilege) | Four DB users with different permissions; what each can and cannot do |
| 2 | Parameterised queries | SQL injection succeeding against string-built SQL and failing against parameters |
| 3 | Audit log (triggers) | Who changed what and when, and staff cannot erase the trail |
| 4 | Authentication | Salted PBKDF2 password hashes and a safe, parameterised login |

Everything runs only against the `zuct_records` database that the scripts create.
All data is fictional.

## Tools

* MariaDB 10.x (MySQL-compatible; XAMPP's MySQL/MariaDB works)
* Python 3.9+ with the `pymysql` package (`pip install pymysql`)

## Folder layout

```
sql/01_schema.sql                 tables: students, courses, grades, app_users, audit_log
sql/02_sample_data.sql            fictional sample data
sql/03_users_and_privileges.sql   database users and their GRANTs
sql/04_audit_triggers.sql         triggers that fill audit_log
app/common.py                     connection helper, PBKDF2 hashing, secure login
app/demo_1_permissions.py         access-control tests (24 checks)
app/demo_2_sql_injection.py       vulnerable vs parameterised search
app/demo_3_audit_log.py           audit trail and tamper attempts
app/demo_4_authentication.py      hashed passwords and login attempts
setup.py                          builds everything with one command
run_demos.py                      runs all four demos
sample_output.txt                 output of a full run (for the slides)
```

## How to run

1. Start MariaDB/MySQL (in XAMPP, start the MySQL module).
2. Install the driver: `pip install pymysql`
3. Build the database: `python setup.py`
   * Uses the `mysql` client as `root`. If your root has a password or the
     client is elsewhere: `MYSQL_ARGS="-u root -p"` and/or `MYSQL_BIN="C:\xampp\mysql\bin\mysql.exe"`
     (on Windows PowerShell: `$env:MYSQL_ARGS="-u root"`).
4. Run the demos: `python run_demos.py` (or run any `app/demo_*.py` on its own).

`setup.py` rebuilds the database from scratch, so you can run it again at any
time to reset the sample data.

## Database accounts (demo passwords)

| Account | Password | Can | Cannot |
|---------|----------|-----|--------|
| `db_admin` | `Admin#Demo2026` | Everything in `zuct_records` | Anything outside that database |
| `registrar_user` | `Registrar#Demo2026` | Full CRUD on students and courses; read grades | Change marks, read `app_users`, read/modify `audit_log`, drop tables |
| `lecturer_user` | `Lecturer#Demo2026` | Read name/programme/year; read, enter and correct marks | Read phone/NRC/fees, delete grades, edit students, read `audit_log` |
| `auditor_user` | `Auditor#Demo2026` | Read `audit_log` | Everything else |
| `app_service` | `AppSvc#Demo2026` | Read a few student columns and `app_users` (for login) | Write anything, read phone/NRC/fees |

Application logins (table `app_users`): `registrar1` / `Registrar@123`,
`lecturer1` / `Lecturer@123`, `auditor1` / `Auditor@123`.

These passwords exist only for the throw-away demo database. In a real system,
use strong unique secrets held in environment variables or a secrets manager.

## How each measure works

**Access control.** Accounts are created with only the privileges their job needs
(`GRANT ... ON table`). The lecturer account uses a *column-level* grant, so
`SELECT phone FROM students` fails and so does `SELECT *`.

**Parameterised queries.** `search_vulnerable()` builds SQL with an f-string, so
input such as `x' OR '1'='1' -- -` changes the meaning of the query.
`search_secure()` keeps the SQL text fixed and passes input as parameters (`%s`),
so the same input is treated as a harmless name. Note: PyMySQL escapes parameters
on the client; the server-side equivalent is a prepared statement. Both keep data
and code separate.

**Audit log.** `AFTER INSERT/UPDATE/DELETE` triggers on `students` and `grades`
write the user (`USER()`), time, action and old/new values to `audit_log`.
Triggers run with their definer's rights, so staff need no privilege on
`audit_log` and cannot read, edit or delete it. Phone and NRC values are never
copied into the log.

**Authentication.** Passwords are stored as `pbkdf2_sha256$600000$salt$hash`
(random 16-byte salt, 600,000 iterations), compared in constant time.

## Troubleshooting

* *Access denied for a demo user* - with XAMPP, an anonymous `''@'localhost'`
  account can take priority over the demo users. Remove it with
  `DROP USER ''@'localhost';` (only on your own practice server) and run `setup.py` again.
* *Can't connect* - check MySQL is running; set `DB_HOST` / `DB_PORT` if it is not on `localhost:3306`.

## Known limitations (good discussion points)

* A user with `db_admin` rights could still tamper with `audit_log`; production
  systems ship logs to a separate, append-only store or use the MariaDB audit plugin.
* No TLS between app and database, no encryption at rest, and no account lockout
  in this small prototype; these are covered in the presentation as further work.
