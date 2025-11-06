# db/database.py
import sqlite3
from contextlib import contextmanager
from db.database import get_connection
from db.models import TABLES

DB_PATH = "data/canvas_data.db"

@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()


def init_db():
    with get_connection() as conn:
        cur = conn.cursor()
        for ddl in TABLES.values():
            cur.execute(ddl)
