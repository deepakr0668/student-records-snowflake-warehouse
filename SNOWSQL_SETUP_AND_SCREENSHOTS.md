# SnowSQL Setup and Screenshot Evidence

## 1. Install and configure SnowSQL

Install SnowSQL from the Snowflake documentation, then run `snowsql -a <organization-account> -u <username> -r <role> -w STUDENT_WH`. Snowflake will prompt for your password; never add it to a project file or screenshot.

After connecting, run the first query in `snowflake_tutorial_assignment.sql`. It displays the current user, role, warehouse, database, and schema.

## 2. Loading the CSV

Before executing the `PUT` command, replace `C:/path/to/students.csv` with the real absolute path of this project's `students.csv`. Execute the `PUT`, `LIST`, `COPY INTO`, `COUNT(*)`, and sample `SELECT` commands in sequence.

## 3. Required screenshots for submission

Capture clear screenshots from Snowsight or a SnowSQL terminal. Each screenshot must show both the executed SQL and its output.

1. **Connection proof:** `CURRENT_USER`, `CURRENT_ROLE`, `CURRENT_WAREHOUSE`, `CURRENT_DATABASE`, and `CURRENT_SCHEMA` output.
2. **Objects and DML:** successful `CREATE` statements plus the `SELECT` result after insert/update/delete.
3. **CSV loading:** `PUT`/`COPY INTO` result plus `COUNT(*)` confirming 50 records.
4. **Time Travel query:** the historical query showing `S015` and `S016` with the original mark of 77.
5. **Recovery proof:** final `SELECT` showing `S015` restored after the `INSERT ... AT (TIMESTAMP ...)` query.

Save them as `screenshots/01_connection.png` through `screenshots/05_recovery.png`. They cannot be generated truthfully without access to your Snowflake account.
