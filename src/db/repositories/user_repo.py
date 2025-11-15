import sqlite3
import logging
from db.database import get_connection

logger = logging.getLogger(__name__)

class UserRepository:
    def __init__(self):
        self.conn = get_connection()
        self.conn.row_factory = sqlite3.Row

    def upsert(self, user_id, name, sis_id=None, email=None):
        """Insert or update a user record."""
        try:
            self.conn.execute("""
                INSERT INTO user_store (user_id, name, sis_id, email)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    name = excluded.name,
                    sis_id = excluded.sis_id,
                    email = excluded.email
            """, (user_id, name, sis_id, email))
            self.conn.commit()
            logger.debug(f"Upserted user {user_id}: {name}")
        except Exception as e:
            logger.error(f"Error inserting/updating user {user_id}: {e}")

    def get_user(self, user_id):
        cur = self.conn.execute("SELECT * FROM user_store WHERE user_id = ?", (str(user_id),))
        return cur.fetchone()

    def list_all(self):
        cur = self.conn.execute("SELECT * FROM user_store ORDER BY name")
        return [dict(row) for row in cur.fetchall()]