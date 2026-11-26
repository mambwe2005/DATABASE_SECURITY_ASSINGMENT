-- =====================================================================
-- BIT3360 Advanced Databases - Database Security prototype
-- 01_schema.sql : creates the demo database and its tables
-- Run as a privileged account (e.g. root). Safe to re-run: it rebuilds
-- the demo database from scratch. Only touches the zuct_records database.
-- =====================================================================

DROP DATABASE IF EXISTS zuct_records;
CREATE DATABASE zuct_records
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
USE zuct_records;

-- Students: contains personal data (phone, NRC, fees) that not every
-- user should be able to see.
CREATE TABLE students (
  student_id    INT AUTO_INCREMENT PRIMARY KEY,
  first_name    VARCHAR(50)  NOT NULL,
  last_name     VARCHAR(50)  NOT NULL,
  email         VARCHAR(100) NOT NULL UNIQUE,
  phone         VARCHAR(20),
  nrc_number    VARCHAR(20),                       -- sensitive (sample data only)
  programme     VARCHAR(10)  NOT NULL,             -- BIT, BBA, BENG
  year_of_study TINYINT      NOT NULL,
  fees_balance  DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT chk_year CHECK (year_of_study BETWEEN 1 AND 5)
) ENGINE=InnoDB;

CREATE TABLE courses (
  course_code VARCHAR(10)  PRIMARY KEY,
  title       VARCHAR(100) NOT NULL,
  credits     TINYINT      NOT NULL
) ENGINE=InnoDB;

CREATE TABLE grades (
  grade_id      INT AUTO_INCREMENT PRIMARY KEY,
  student_id    INT           NOT NULL,
  course_code   VARCHAR(10)   NOT NULL,
  mark          DECIMAL(5,2)  NOT NULL,
  academic_year VARCHAR(9)    NOT NULL,
  CONSTRAINT fk_grade_student FOREIGN KEY (student_id)  REFERENCES students(student_id),
  CONSTRAINT fk_grade_course  FOREIGN KEY (course_code) REFERENCES courses(course_code),
  CONSTRAINT chk_mark CHECK (mark BETWEEN 0 AND 100),
  CONSTRAINT uq_grade UNIQUE (student_id, course_code, academic_year)
) ENGINE=InnoDB;

-- Application logins (used by the Python app, separate from DB accounts).
-- Passwords are NEVER stored in plain text: only a salted PBKDF2 hash.
CREATE TABLE app_users (
  user_id       INT AUTO_INCREMENT PRIMARY KEY,
  username      VARCHAR(50)  NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role          ENUM('registrar','lecturer','auditor') NOT NULL,
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Audit trail: filled automatically by triggers (see 04_audit_triggers.sql).
CREATE TABLE audit_log (
  log_id     BIGINT AUTO_INCREMENT PRIMARY KEY,
  table_name VARCHAR(50)  NOT NULL,
  action     ENUM('INSERT','UPDATE','DELETE') NOT NULL,
  record_id  INT          NOT NULL,
  old_values TEXT,
  new_values TEXT,
  db_user    VARCHAR(100) NOT NULL,
  changed_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  INDEX idx_audit_time (changed_at),
  INDEX idx_audit_user (db_user)
) ENGINE=InnoDB;
