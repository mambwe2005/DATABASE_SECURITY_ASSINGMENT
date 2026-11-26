-- =====================================================================
-- 04_audit_triggers.sql : automatic audit log (additional security measure)
--
-- Every INSERT / UPDATE / DELETE on students and grades is recorded in
-- audit_log with WHO (USER()), WHEN (changed_at) and WHAT (old/new values).
--
-- Triggers run with the privileges of their DEFINER (the account that ran
-- this script), so users such as registrar_user or lecturer_user do NOT need
-- any privilege on audit_log. They cannot read, edit or delete the log, yet
-- every change they make is still recorded.
-- Sensitive columns (phone, NRC) are never copied into the log in plain text;
-- an update to them is logged only as a "changed" flag.
-- =====================================================================
USE zuct_records;

DROP TRIGGER IF EXISTS trg_students_ai;
DROP TRIGGER IF EXISTS trg_students_au;
DROP TRIGGER IF EXISTS trg_students_ad;
DROP TRIGGER IF EXISTS trg_grades_ai;
DROP TRIGGER IF EXISTS trg_grades_au;
DROP TRIGGER IF EXISTS trg_grades_ad;

DELIMITER $$

-- ---------------------------- students ------------------------------
CREATE TRIGGER trg_students_ai AFTER INSERT ON students
FOR EACH ROW
BEGIN
  INSERT INTO audit_log (table_name, action, record_id, old_values, new_values, db_user)
  VALUES ('students', 'INSERT', NEW.student_id, NULL,
          JSON_OBJECT('first_name', NEW.first_name, 'last_name', NEW.last_name,
                      'email', NEW.email, 'programme', NEW.programme,
                      'year_of_study', NEW.year_of_study,
                      'fees_balance', NEW.fees_balance),
          USER());
END$$

CREATE TRIGGER trg_students_au AFTER UPDATE ON students
FOR EACH ROW
BEGIN
  INSERT INTO audit_log (table_name, action, record_id, old_values, new_values, db_user)
  VALUES ('students', 'UPDATE', NEW.student_id,
          JSON_OBJECT('first_name', OLD.first_name, 'last_name', OLD.last_name,
                      'email', OLD.email, 'programme', OLD.programme,
                      'year_of_study', OLD.year_of_study,
                      'fees_balance', OLD.fees_balance),
          JSON_OBJECT('first_name', NEW.first_name, 'last_name', NEW.last_name,
                      'email', NEW.email, 'programme', NEW.programme,
                      'year_of_study', NEW.year_of_study,
                      'fees_balance', NEW.fees_balance,
                      'phone_changed', IF(OLD.phone <=> NEW.phone, 'no', 'yes'),
                      'nrc_changed',   IF(OLD.nrc_number <=> NEW.nrc_number, 'no', 'yes')),
          USER());
END$$

CREATE TRIGGER trg_students_ad AFTER DELETE ON students
FOR EACH ROW
BEGIN
  INSERT INTO audit_log (table_name, action, record_id, old_values, new_values, db_user)
  VALUES ('students', 'DELETE', OLD.student_id,
          JSON_OBJECT('first_name', OLD.first_name, 'last_name', OLD.last_name,
                      'email', OLD.email, 'programme', OLD.programme,
                      'year_of_study', OLD.year_of_study,
                      'fees_balance', OLD.fees_balance),
          NULL, USER());
END$$

-- ----------------------------- grades -------------------------------
CREATE TRIGGER trg_grades_ai AFTER INSERT ON grades
FOR EACH ROW
BEGIN
  INSERT INTO audit_log (table_name, action, record_id, old_values, new_values, db_user)
  VALUES ('grades', 'INSERT', NEW.grade_id, NULL,
          JSON_OBJECT('student_id', NEW.student_id, 'course_code', NEW.course_code,
                      'mark', NEW.mark, 'academic_year', NEW.academic_year),
          USER());
END$$

CREATE TRIGGER trg_grades_au AFTER UPDATE ON grades
FOR EACH ROW
BEGIN
  INSERT INTO audit_log (table_name, action, record_id, old_values, new_values, db_user)
  VALUES ('grades', 'UPDATE', NEW.grade_id,
          JSON_OBJECT('student_id', OLD.student_id, 'course_code', OLD.course_code,
                      'mark', OLD.mark, 'academic_year', OLD.academic_year),
          JSON_OBJECT('student_id', NEW.student_id, 'course_code', NEW.course_code,
                      'mark', NEW.mark, 'academic_year', NEW.academic_year),
          USER());
END$$

CREATE TRIGGER trg_grades_ad AFTER DELETE ON grades
FOR EACH ROW
BEGIN
  INSERT INTO audit_log (table_name, action, record_id, old_values, new_values, db_user)
  VALUES ('grades', 'DELETE', OLD.grade_id,
          JSON_OBJECT('student_id', OLD.student_id, 'course_code', OLD.course_code,
                      'mark', OLD.mark, 'academic_year', OLD.academic_year),
          NULL, USER());
END$$

DELIMITER ;
