-- =====================================================================
-- 03_users_and_privileges.sql : database accounts and what each may do
-- Principle of least privilege: every account gets only what its job needs.
--
-- NOTE: the passwords below are DEMO passwords for a throw-away database.
-- In a real system, use strong unique secrets kept in a secrets manager or
-- environment variables, never in source control.
-- =====================================================================

DROP USER IF EXISTS 'db_admin'@'localhost';
DROP USER IF EXISTS 'registrar_user'@'localhost';
DROP USER IF EXISTS 'lecturer_user'@'localhost';
DROP USER IF EXISTS 'auditor_user'@'localhost';
DROP USER IF EXISTS 'app_service'@'localhost';

CREATE USER 'db_admin'@'localhost'       IDENTIFIED BY 'Admin#Demo2026';
CREATE USER 'registrar_user'@'localhost' IDENTIFIED BY 'Registrar#Demo2026';
CREATE USER 'lecturer_user'@'localhost'  IDENTIFIED BY 'Lecturer#Demo2026';
CREATE USER 'auditor_user'@'localhost'   IDENTIFIED BY 'Auditor#Demo2026';
CREATE USER 'app_service'@'localhost'    IDENTIFIED BY 'AppSvc#Demo2026';

-- 1) Administrator: full control of the demo database only (not the server).
GRANT ALL PRIVILEGES ON zuct_records.* TO 'db_admin'@'localhost';

-- 2) Registrar: manages student and course records, can READ grades,
--    but cannot change marks, touch app logins or read/modify the audit log.
GRANT SELECT, INSERT, UPDATE, DELETE ON zuct_records.students TO 'registrar_user'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON zuct_records.courses  TO 'registrar_user'@'localhost';
GRANT SELECT                         ON zuct_records.grades   TO 'registrar_user'@'localhost';

-- 3) Lecturer: enters and corrects marks. Sees only the non-sensitive student
--    columns (column-level privilege) and can never DELETE a grade.
GRANT SELECT (student_id, first_name, last_name, programme, year_of_study)
      ON zuct_records.students TO 'lecturer_user'@'localhost';
GRANT SELECT                   ON zuct_records.courses  TO 'lecturer_user'@'localhost';
GRANT SELECT, INSERT, UPDATE   ON zuct_records.grades   TO 'lecturer_user'@'localhost';

-- 4) Auditor: read-only access to the audit trail and nothing else.
GRANT SELECT ON zuct_records.audit_log TO 'auditor_user'@'localhost';

-- 5) Application service account (used by the Python app): can search a few
--    non-sensitive student columns and read app logins to check passwords.
--    No INSERT/UPDATE/DELETE, no DDL, no access to phone/NRC/fees.
GRANT SELECT (student_id, first_name, last_name, programme)
      ON zuct_records.students  TO 'app_service'@'localhost';
GRANT SELECT ON zuct_records.app_users TO 'app_service'@'localhost';

FLUSH PRIVILEGES;
