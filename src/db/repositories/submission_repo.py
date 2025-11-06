import sqlite3
import logging
from db.database import get_connection

logger = logging.getLogger(__name__)

class SubmissionRepository:
    def __init__(self):
        self.conn = get_connection()
        self.conn.row_factory = sqlite3.Row

    def upsert(self, sub):
        """Insert or update a submission record."""
        try:
            self.conn.execute("""
                INSERT INTO submission_store (user_id, course_id, quiz_id, extra_time, extra_attempts, date)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id, course_id, quiz_id) DO UPDATE SET
                    extra_time = excluded.extra_time,
                    extra_attempts = excluded.extra_attempts,
                    date = excluded.date
            """, (
                str(sub["user_id"]),
                str(sub["course_id"]),
                str(sub["quiz_id"]),
                float(sub.get("extra_time", 0)),
                int(sub.get("extra_attempts", 0)),
                sub.get("date", "")
            ))
            self.conn.commit()
            logger.info(f"Upserted submission: user={sub['user_id']}, course={sub['course_id']}, quiz={sub['quiz_id']}")
        except Exception as e:
            logger.error(f"Error upserting submission: {e}")

    def get_submission(self, user_id, course_id, quiz_id):
        cur = self.conn.execute("""
            SELECT * FROM submission_store
            WHERE user_id = ? AND course_id = ? AND quiz_id = ?
        """, (str(user_id), str(course_id), str(quiz_id)))
        return cur.fetchone()

    def get_submissions_by_user(self, user_id):
        cur = self.conn.execute("SELECT * FROM submission_store WHERE user_id = ?", (str(user_id),))
        return [dict(row) for row in cur.fetchall()]

    def list_all(self):
        cur = self.conn.execute("SELECT * FROM submission_store")
        return [dict(row) for row in cur.fetchall()]
