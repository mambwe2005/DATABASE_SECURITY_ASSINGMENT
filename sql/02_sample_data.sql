-- =====================================================================
-- 02_sample_data.sql : fictional sample data (no real people)
-- =====================================================================
USE zuct_records;

INSERT INTO students (first_name, last_name, email, phone, nrc_number, programme, year_of_study, fees_balance) VALUES
('Chanda',   'Mulenga', 'chanda.mulenga@student.example',  '0970000001', '100001/10/1', 'BIT',  3,  1500.00),
('Mwila',    'Banda',   'mwila.banda@student.example',     '0970000002', '100002/10/1', 'BIT',  3,     0.00),
('Thandiwe', 'Phiri',   'thandiwe.phiri@student.example',  '0970000003', '100003/10/1', 'BIT',  2,  3200.50),
('Kabwe',    'Tembo',   'kabwe.tembo@student.example',     '0970000004', '100004/10/1', 'BBA',  1,   800.00),
('Namukolo', 'Zulu',    'namukolo.zulu@student.example',   '0970000005', '100005/10/1', 'BIT',  4,     0.00),
('Mutale',   'Chanda',  'mutale.chanda@student.example',   '0970000006', '100006/10/1', 'BENG', 2,  2100.00),
('Bupe',     'Mwansa',  'bupe.mwansa@student.example',     '0970000007', '100007/10/1', 'BBA',  3,   450.75),
('Chileshe', 'Sakala',  'chileshe.sakala@student.example', '0970000008', '100008/10/1', 'BIT',  1,  4000.00),
('Lubono',   'Mumba',   'lubono.mumba@student.example',    '0970000009', '100009/10/1', 'BENG', 4,     0.00),
('Natasha',  'Daka',    'natasha.daka@student.example',    '0970000010', '100010/10/1', 'BIT',  3,   975.00);

INSERT INTO courses (course_code, title, credits) VALUES
('BIT3360', 'Advanced Databases',        4),
('BIT3320', 'Computer Networks',         4),
('BIT3340', 'Web Application Development', 4),
('BIT3350', 'Systems Analysis and Design', 3),
('BIT3380', 'Information Security',      3);

INSERT INTO grades (student_id, course_code, mark, academic_year) VALUES
(1, 'BIT3360', 72.50, '2025/2026'),
(1, 'BIT3320', 65.00, '2025/2026'),
(1, 'BIT3380', 58.00, '2025/2026'),
(2, 'BIT3360', 81.00, '2025/2026'),
(2, 'BIT3340', 77.50, '2025/2026'),
(2, 'BIT3380', 69.00, '2025/2026'),
(3, 'BIT3320', 48.00, '2025/2026'),
(3, 'BIT3350', 55.50, '2025/2026'),
(5, 'BIT3360', 90.00, '2025/2026'),
(5, 'BIT3380', 84.00, '2025/2026'),
(8, 'BIT3340', 61.00, '2025/2026'),
(10,'BIT3360', 74.00, '2025/2026'),
(10,'BIT3320', 70.50, '2025/2026');
