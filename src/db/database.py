import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / "data.db"
_CONN = None  # global lazy connection

def get_connection():
    """Return a singleton SQLite connection with row factory."""
    global _CONN
    if _CONN is None:
        _CONN = sqlite3.connect(DB_PATH)
        _CONN.row_factory = sqlite3.Row
        logger.info(f"Connected to SQLite database at {DB_PATH}")
    return _CONN

def close_connection():
    """Close active connection if open."""
    global _CONN
    if _CONN:
        _CONN.close()
        _CONN = None
        logger.info("Closed SQLite connection.")

def initialize_database():
    """Load schema from schema.sql, creating database if needed."""
    schema_path = Path(__file__).parent / "models/schema.sql"
    conn = get_connection()
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
        conn.executescript(schema_sql)
        conn.commit()
    logger.info("Database initialized successfully.")
