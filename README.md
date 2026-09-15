# Student Records: SnowSQL Tutorial Assignment

This project includes a 50-student `students.csv` plus an assignment-ready SnowSQL script for object creation, CSV staging/loading, Time Travel, and recovery. It also retains a local ETL/warehouse model for preprocessing, OLAP, data mining, and visualization.

## Start here for the tutorial

Run [snowflake_tutorial_assignment.sql](snowflake_tutorial_assignment.sql) in SnowSQL, following [SNOWSQL_SETUP_AND_SCREENSHOTS.md](SNOWSQL_SETUP_AND_SCREENSHOTS.md). This produces the SQL and real account output needed for all five questions. The screenshots must be captured after you run the commands in your own Snowflake account.

## Architecture

`students.csv` -> extraction/validation -> preprocessing -> dimensions + fact table -> OLAP/data mining -> CSV/chart outputs

The warehouse uses a normalized snowflake schema, ready to translate to Snowflake SQL:

- `dim_student`: student identity
- `dim_course`: course lookup
- `dim_department`: parent lookup for courses
- `dim_date`: enrollment calendar
- `fact_student_performance`: marks, grade, and performance band

`student_warehouse.py` uses SQLite so the model works without a Snowflake account. `warehouse.sql` provides Snowflake DDL/OLAP SQL for deployment.

## Run local ETL model

```powershell
pip install -r requirements.txt
python student_warehouse.py
```

Outputs generated: `student_warehouse.db`, `olap_course_quarter.csv`, `mining_student_segments.csv`, and `student_analytics.png`.

## ETL and analytics

Preprocessing removes duplicate student IDs, rejects missing/invalid values, constrains marks to 0–100, parses dates, and derives grade, performance band, and date key. The OLAP query summarizes average marks and student counts by course/year/quarter. A dependency-free K-Means routine creates three performance segments from standardized marks.

## Update, delete, and recovery

The `demo_dml()` function updates `S003` to 92, temporarily deletes dropped student `S015`, and restores them from a recovery table. In Snowflake, the tutorial script uses Time Travel to recover deleted records.
