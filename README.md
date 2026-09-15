# Student Records: Snowflake Warehouse Model

This runnable assignment loads a 50-student `students.csv`, cleans it, builds a dimensional warehouse, produces OLAP output, segments students with K-Means, and renders charts.

## Architecture

`students.csv` -> extraction/validation -> preprocessing -> dimensions + fact table -> OLAP/data mining -> CSV/chart outputs

The warehouse uses a normalized snowflake schema, ready to translate to Snowflake SQL:

- `dim_student`: student identity
- `dim_course`: course lookup
- `dim_department`: parent lookup for courses (normalizes the course hierarchy)
- `dim_date`: enrollment calendar
- `fact_student_performance`: marks, grade, and performance band

`student_warehouse.py` uses SQLite so the model works without a Snowflake account. `warehouse.sql` provides Snowflake DDL/OLAP SQL for deployment.

## Run

```powershell
pip install -r requirements.txt
python student_warehouse.py
```

Outputs generated: `student_warehouse.db`, `olap_course_quarter.csv`, `mining_student_segments.csv`, and `student_analytics.png`.

## ETL and analytics

Preprocessing removes duplicate student IDs, rejects missing/invalid values, constrains marks to 0–100, parses dates, and derives grade, performance band, and date key. The OLAP query summarizes average marks and student counts by course/year/quarter. A dependency-free K-Means routine creates three performance segments from standardized marks.

## Demonstrating update, delete, recovery

The `demo_dml()` function updates `S003` to 92, temporarily deletes dropped student `S015`, and restores them from a recovery table. In Snowflake, use Time Travel (illustrated in `warehouse.sql`) to recover deleted records within the retention period.
