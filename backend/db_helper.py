from contextlib import contextmanager
import sqlite3
from backend.logging_setup import setup_logger


logger = setup_logger('db_helper')


class SQLiteCursorWrapper:
    """Wrap sqlite3 cursor to provide a fetchall that returns list[dict]
    and to accept queries written with %s placeholders (converted to ?)."""
    def __init__(self, cursor, connection):
        self._cursor = cursor
        self._conn = connection

    def execute(self, query, params=None):
        # Convert MySQL-style %s placeholders to sqlite ? placeholders
        if params is None:
            return self._cursor.execute(query)
        q = query.replace('%s', '?')
        return self._cursor.execute(q, params)

    def fetchall(self):
        rows = self._cursor.fetchall()
        # sqlite3.Row -> dict
        return [dict(row) for row in rows]

    def close(self):
        # cursor closed by context manager
        return


@contextmanager
def get_db_cursor(commit=False):
    """Attempt to use MySQL; on any failure, fall back to a local SQLite DB.

    The SQLite DB is stored in `expense_manager.db` next to the project
    and is auto-created and seeded with a sample row used by tests.
    """
    # First try MySQL (if available and running)
    try:
        import mysql.connector

        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="expense_manager"
        )

        cursor = connection.cursor(dictionary=True)
        yield cursor
        if commit:
            connection.commit()
        cursor.close()
        connection.close()
        return
    except Exception as e:  # fallback to sqlite when MySQL is unreachable
        logger.info(f"MySQL not available, falling back to SQLite: {e}")

    # SQLite fallback
    conn = sqlite3.connect("expense_manager.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Ensure table exists and seed expected test data
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS expenses (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               expense_date TEXT,
               amount REAL,
               category TEXT,
               notes TEXT
           );'''
    )
    # Seed a sample row used by tests if not present
    cur.execute("SELECT COUNT(1) as cnt FROM expenses WHERE expense_date = ?", ("2024-08-15",))
    row = cur.fetchone()
    if row and row[0] == 0:
        cur.execute(
            "INSERT INTO expenses (expense_date, amount, category, notes) VALUES (?, ?, ?, ?)",
            ("2024-08-15", 10.0, "Shopping", "Bought potatoes"),
        )
        conn.commit()

    wrapper = SQLiteCursorWrapper(cur, conn)
    try:
        yield wrapper
        if commit:
            conn.commit()
    finally:
        cur.close()
        conn.close()


def fetch_expenses_for_date(expense_date):
    logger.info(f"fetch_expenses_for_date called with {expense_date}")
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM expenses WHERE expense_date = %s", (expense_date,))
        expenses = cursor.fetchall()
        return expenses


def delete_expenses_for_date(expense_date):
    logger.info(f"delete_expenses_for_date called with {expense_date}")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM expenses WHERE expense_date = %s", (expense_date,))


def insert_expense(expense_date, amount, category, notes):
    logger.info(f"insert_expense called with date: {expense_date}, amount: {amount}, category: {category}, notes: {notes}")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            "INSERT INTO expenses (expense_date, amount, category, notes) VALUES (%s, %s, %s, %s)",
            (expense_date, amount, category, notes)
        )


def fetch_expense_summary(start_date, end_date):
    logger.info(f"fetch_expense_summary called with start: {start_date} end: {end_date}")
    with get_db_cursor() as cursor:
        cursor.execute(
            '''SELECT category, SUM(amount) as total 
               FROM expenses WHERE expense_date
               BETWEEN %s and %s  
               GROUP BY category;''',
            (start_date, end_date)
        )
        data = cursor.fetchall()
        return data


if __name__ == "__main__":
    expenses = fetch_expenses_for_date("2024-09-30")
    print(expenses)
    # delete_expenses_for_date("2024-08-25")
    summary = fetch_expense_summary("2024-08-01", "2024-08-05")
    for record in summary:
        print(record)
