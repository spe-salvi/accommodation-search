import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / "data.db"

def get_connection():
    """Return a singleton SQLite connection with row factory."""
    conn = getattr(get_connection, "_conn", None)
    if conn is None:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        get_connection._conn = conn
        logger.info(f"Connected to SQLite database at {DB_PATH}")
    return conn

def initialize_database():
    """Load schema from schema.sql."""
    schema_path = Path(__file__).parent / "models/schema.sql"
    conn = get_connection()
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
        conn.executescript(schema_sql)
        conn.commit()
    logger.info("Database initialized successfully.")
