-- Snowflake SQL version of the warehouse model.
CREATE OR REPLACE DATABASE STUDENT_ANALYTICS;
CREATE OR REPLACE SCHEMA STUDENT_ANALYTICS.WAREHOUSE;
USE SCHEMA STUDENT_ANALYTICS.WAREHOUSE;

CREATE OR REPLACE TABLE dim_course (
  course_key INTEGER AUTOINCREMENT, course_name STRING UNIQUE, department_key INTEGER
);
CREATE OR REPLACE TABLE dim_department (
  department_key INTEGER AUTOINCREMENT, department_name STRING UNIQUE
);
CREATE OR REPLACE TABLE dim_date (
  date_key INTEGER, enrollment_date DATE, year INTEGER, quarter INTEGER, month INTEGER
);
CREATE OR REPLACE TABLE dim_student (
  student_key INTEGER AUTOINCREMENT, student_id STRING UNIQUE, student_name STRING
);
CREATE OR REPLACE TABLE fact_student_performance (
  student_key INTEGER, course_key INTEGER, date_key INTEGER, marks NUMBER(5,2),
  grade STRING, performance_band STRING
);

-- OLAP: average marks by course and enrollment quarter.
SELECT c.course_name, d.year, d.quarter, ROUND(AVG(f.marks),2) AS avg_marks,
       COUNT(*) AS students
FROM fact_student_performance f
JOIN dim_course c ON f.course_key=c.course_key
JOIN dim_department dp ON c.department_key=dp.department_key
JOIN dim_date d ON f.date_key=d.date_key
GROUP BY ROLLUP(dp.department_name, c.course_name, d.year, d.quarter)
ORDER BY dp.department_name, c.course_name, d.year, d.quarter;

-- Controlled recovery demonstration (Time Travel; retention policy permitting).
-- DELETE FROM dim_student WHERE student_id='S015';
-- SELECT * FROM dim_student AT (OFFSET => -60) WHERE student_id='S015';
