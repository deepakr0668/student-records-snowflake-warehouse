"""End-to-end CSV -> warehouse -> OLAP -> data mining project."""
from pathlib import Path
import os
import sqlite3
ROOT = Path(__file__).parent
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".matplotlib"))
import pandas as pd
import matplotlib.pyplot as plt

DATA = ROOT / "students.csv"
DB = ROOT / "student_warehouse.db"
CHART = ROOT / "student_analytics.png"

def grade(marks):
    if marks >= 90: return "A+"
    if marks >= 80: return "A"
    if marks >= 70: return "B"
    if marks >= 60: return "C"
    return "D"

def band(marks):
    if marks >= 85: return "High"
    if marks >= 70: return "Medium"
    return "Needs support"

def extract_transform():
    df = pd.read_csv(DATA)
    required = {"student_id", "name", "course", "marks", "enrollment_date"}
    if set(df.columns) != required:
        raise ValueError(f"CSV must contain exactly: {sorted(required)}")
    df = df.drop_duplicates("student_id").dropna()
    df["marks"] = pd.to_numeric(df["marks"], errors="raise").clip(0, 100)
    df["enrollment_date"] = pd.to_datetime(df["enrollment_date"], errors="raise")
    df["grade"] = df.marks.map(grade)
    df["performance_band"] = df.marks.map(band)
    df["date_key"] = df.enrollment_date.dt.strftime("%Y%m%d").astype(int)
    return df

def load(df):
    with sqlite3.connect(DB) as con:
        con.executescript("""
        DROP TABLE IF EXISTS fact_student_performance;
        DROP TABLE IF EXISTS dim_student; DROP TABLE IF EXISTS dim_course; DROP TABLE IF EXISTS dim_department; DROP TABLE IF EXISTS dim_date;
        CREATE TABLE dim_student (student_key INTEGER PRIMARY KEY, student_id TEXT UNIQUE, student_name TEXT);
        CREATE TABLE dim_department (department_key INTEGER PRIMARY KEY, department_name TEXT UNIQUE);
        CREATE TABLE dim_course (course_key INTEGER PRIMARY KEY, course_name TEXT UNIQUE, department_key INTEGER);
        CREATE TABLE dim_date (date_key INTEGER PRIMARY KEY, enrollment_date TEXT, year INTEGER, quarter INTEGER, month INTEGER);
        CREATE TABLE fact_student_performance (student_key INTEGER, course_key INTEGER, date_key INTEGER, marks REAL, grade TEXT, performance_band TEXT);
        """)
        students = df[["student_id", "name"]].drop_duplicates().rename(columns={"name":"student_name"})
        students.to_sql("dim_student", con, if_exists="append", index=False)
        # A snowflake-schema normalization: course rolls up to a department.
        departments = pd.DataFrame({"department_name": ["Technology"]})
        departments.to_sql("dim_department", con, if_exists="append", index=False)
        courses = df[["course"]].drop_duplicates().rename(columns={"course":"course_name"})
        courses["department_key"] = int(pd.read_sql("SELECT department_key FROM dim_department", con).iloc[0, 0])
        courses.to_sql("dim_course", con, if_exists="append", index=False)
        dates = pd.DataFrame({"date_key":df.date_key, "enrollment_date":df.enrollment_date.dt.date.astype(str),
                              "year":df.enrollment_date.dt.year, "quarter":df.enrollment_date.dt.quarter,
                              "month":df.enrollment_date.dt.month}).drop_duplicates()
        dates.to_sql("dim_date", con, if_exists="append", index=False)
        fact = df.merge(pd.read_sql("SELECT * FROM dim_student", con), on="student_id").merge(
            pd.read_sql("SELECT * FROM dim_course", con), left_on="course", right_on="course_name")
        fact[["student_key","course_key","date_key","marks","grade","performance_band"]].to_sql("fact_student_performance", con, if_exists="append", index=False)

def olap_and_mining():
    with sqlite3.connect(DB) as con:
        olap = pd.read_sql_query("""
        SELECT c.course_name AS course, d.year, d.quarter, ROUND(AVG(f.marks),2) AS average_marks,
               COUNT(*) AS student_count
        FROM fact_student_performance f JOIN dim_course c USING(course_key) JOIN dim_date d USING(date_key)
        GROUP BY c.course_name, d.year, d.quarter ORDER BY course, year, quarter""", con)
        olap.to_csv(ROOT / "olap_course_quarter.csv", index=False)
        detail = pd.read_sql_query("""SELECT s.student_id, s.student_name, c.course_name, f.marks,
        f.grade, f.performance_band FROM fact_student_performance f JOIN dim_student s USING(student_key)
        JOIN dim_course c USING(course_key)""", con)
    # Dependency-free one-dimensional K-Means on standardized marks.
    values = detail["marks"].astype(float).tolist()
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    scale = variance ** 0.5 or 1
    z = [(v - mean) / scale for v in values]
    centroids = [min(z), sorted(z)[len(z) // 2], max(z)]
    for _ in range(30):
        labels = [min(range(3), key=lambda i: abs(value - centroids[i])) for value in z]
        updated = [sum(v for v, label in zip(z, labels) if label == i) / labels.count(i)
                   if i in labels else centroids[i] for i in range(3)]
        if all(abs(a - b) < 0.0001 for a, b in zip(centroids, updated)):
            break
        centroids = updated
    detail["cluster"] = labels
    detail.to_csv(ROOT / "mining_student_segments.csv", index=False)
    return olap, detail

def charts(olap, detail):
    plt.style.use("ggplot")
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    course_means = olap.groupby("course", as_index=False)["average_marks"].mean()
    axes[0].bar(course_means["course"], course_means["average_marks"], color="#3b82f6")
    axes[0].set_title("Average marks by course"); axes[0].set_ylim(0, 100); axes[0].tick_params(axis="x", rotation=25)
    course_codes = {course: index for index, course in enumerate(sorted(detail.course_name.unique()))}
    axes[1].scatter(detail.course_name.map(course_codes), detail.marks, c=detail.cluster, cmap="viridis", s=100)
    axes[1].set_xticks(list(course_codes.values()), list(course_codes.keys()))
    axes[1].set_title("Student performance clusters"); axes[1].set_ylim(0, 100); axes[1].tick_params(axis="x", rotation=25)
    plt.tight_layout(); plt.savefig(CHART, dpi=180); plt.close()

def demo_dml():
    # Example transactional lifecycle: update a mark, delete a dropped student, recover from audit copy.
    with sqlite3.connect(DB) as con:
        con.execute("CREATE TABLE IF NOT EXISTS student_recovery AS SELECT * FROM dim_student WHERE 0")
        con.execute("UPDATE fact_student_performance SET marks=92, grade='A+', performance_band='High' WHERE student_key=(SELECT student_key FROM dim_student WHERE student_id='S003')")
        con.execute("INSERT OR REPLACE INTO student_recovery SELECT * FROM dim_student WHERE student_id='S015'")
        con.execute("DELETE FROM dim_student WHERE student_id='S015'")
        con.execute("INSERT OR IGNORE INTO dim_student SELECT * FROM student_recovery WHERE student_id='S015'")

if __name__ == "__main__":
    cleaned = extract_transform(); load(cleaned); olap, detail = olap_and_mining(); charts(olap, detail); demo_dml()
    print(f"Complete: {len(cleaned)} records loaded; outputs saved in {ROOT}")
