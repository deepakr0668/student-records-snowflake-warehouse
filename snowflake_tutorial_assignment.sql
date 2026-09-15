-- Snowflake Tutorial Assignment: run sections in SnowSQL after configuring your connection.
-- Do not paste account credentials into this file or commit them to GitHub.

-- 1. Verify the SnowSQL connection.
SELECT CURRENT_USER() AS current_user, CURRENT_ROLE() AS current_role,
       CURRENT_WAREHOUSE() AS current_warehouse, CURRENT_DATABASE() AS current_database,
       CURRENT_SCHEMA() AS current_schema;

-- 2. Create Snowflake objects.
CREATE OR REPLACE WAREHOUSE STUDENT_WH
  WAREHOUSE_SIZE = 'XSMALL' AUTO_SUSPEND = 60 AUTO_RESUME = TRUE;
USE WAREHOUSE STUDENT_WH;

CREATE OR REPLACE DATABASE STUDENT_TUTORIAL_DB;
CREATE OR REPLACE SCHEMA STUDENT_TUTORIAL_DB.PUBLIC;
USE DATABASE STUDENT_TUTORIAL_DB;
USE SCHEMA PUBLIC;

CREATE OR REPLACE TABLE STUDENTS (
  student_id VARCHAR(10) PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  course VARCHAR(100) NOT NULL,
  marks NUMBER(5,2) CHECK (marks BETWEEN 0 AND 100),
  enrollment_date DATE
);

CREATE OR REPLACE STAGE STUDENT_CSV_STAGE
  FILE_FORMAT = (TYPE = CSV SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '"');

-- Basic DML. Capture this result for the object/DML screenshot.
INSERT INTO STUDENTS VALUES
 ('S001','Aarav Sharma','Data Engineering',86,'2024-01-15'),
 ('S002','Diya Patel','Data Engineering',91,'2024-01-18'),
 ('S003','Rohan Verma','Cloud Computing',74,'2024-02-02');
SELECT * FROM STUDENTS ORDER BY student_id;
UPDATE STUDENTS SET marks = 92 WHERE student_id = 'S003';
DELETE FROM STUDENTS WHERE student_id = 'S002';
SELECT * FROM STUDENTS ORDER BY student_id;

-- 3. Load the 50-student CSV using SnowSQL.
-- In a SnowSQL terminal, replace the path with the ABSOLUTE path to students.csv.
TRUNCATE TABLE STUDENTS; -- ensures the verification count is exactly 50 after the earlier DML demo.
-- PUT file://C:/path/to/students.csv @STUDENT_CSV_STAGE AUTO_COMPRESS=TRUE OVERWRITE=TRUE;
-- LIST @STUDENT_CSV_STAGE;
-- COPY INTO STUDENTS FROM @STUDENT_CSV_STAGE/students.csv.gz
--   FILE_FORMAT = (TYPE = CSV SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '"')
--   ON_ERROR = 'ABORT_STATEMENT';
-- SELECT COUNT(*) AS loaded_students FROM STUDENTS;
-- SELECT * FROM STUDENTS ORDER BY student_id LIMIT 10;

-- 4. Time Travel demonstration.
CREATE OR REPLACE TABLE STUDENTS_TIME_TRAVEL (
  student_id VARCHAR(10), name VARCHAR(100), course VARCHAR(100),
  marks NUMBER(5,2), enrollment_date DATE
) DATA_RETENTION_TIME_IN_DAYS = 1;

INSERT INTO STUDENTS_TIME_TRAVEL VALUES
 ('S015','Tara Bose','Data Science',81,'2024-07-09'),
 ('S016','Dev Malhotra','Data Engineering',77,'2024-07-18'),
 ('S017','Priya Menon','Cloud Computing',92,'2024-08-02');

-- Save the exact time immediately before the change. Screenshot this query and result.
SET before_changes = CURRENT_TIMESTAMP();
UPDATE STUDENTS_TIME_TRAVEL SET marks = 90 WHERE student_id = 'S016';
DELETE FROM STUDENTS_TIME_TRAVEL WHERE student_id = 'S015';
SELECT * FROM STUDENTS_TIME_TRAVEL ORDER BY student_id;

-- Query the historical version (Time Travel). Screenshot the result showing S015 and original mark 77.
SELECT * FROM STUDENTS_TIME_TRAVEL AT (TIMESTAMP => $before_changes) ORDER BY student_id;

-- 5. Recover accidentally deleted S015 from the historical table state.
INSERT INTO STUDENTS_TIME_TRAVEL
SELECT * FROM STUDENTS_TIME_TRAVEL AT (TIMESTAMP => $before_changes)
WHERE student_id = 'S015';
SELECT * FROM STUDENTS_TIME_TRAVEL ORDER BY student_id;

-- Optional full-table recovery, if an entire table was dropped:
-- DROP TABLE STUDENTS_TIME_TRAVEL;
-- UNDROP TABLE STUDENTS_TIME_TRAVEL;
