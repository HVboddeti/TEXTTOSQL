"""
Database initialisation script for the STUDENT table.

Safe to run multiple times — it will skip creation and inserts
if the table already contains data.
"""

import sqlite3
import sys

DB_PATH = "Student.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS STUDENT (
    Name    VARCHAR(25),
    Class   VARCHAR(25),
    Section VARCHAR(25),
    Marks   INT
);
"""

SEED_DATA = [
    ("Aarav Patel", "10th Grade", "A", 88),
    ("Sophia Williams", "10th Grade", "B", 92),
    ("Liam Johnson", "9th Grade", "A", 76),
    ("Emma Brown", "9th Grade", "C", 84),
    ("Noah Davis", "10th Grade", "A", 95),
]


def init_db(db_path: str = DB_PATH) -> None:
    """Create the STUDENT table and seed it if empty."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create table (IF NOT EXISTS makes this idempotent)
        cursor.execute(SCHEMA)

        # Only insert seed data if the table is empty
        cursor.execute("SELECT COUNT(*) FROM STUDENT")
        count = cursor.fetchone()[0]

        if count == 0:
            cursor.executemany(
                "INSERT INTO STUDENT (Name, Class, Section, Marks) VALUES (?, ?, ?, ?)",
                SEED_DATA,
            )
            print(f"Inserted {len(SEED_DATA)} seed records.")
        else:
            print(f"Table already has {count} records — skipping seed insert.")

        conn.commit()

        # Display current records
        print("\nCurrent records:")
        for row in cursor.execute("SELECT * FROM STUDENT"):
            print(f"  {row}")

    except sqlite3.Error as exc:
        print(f"Database error: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
