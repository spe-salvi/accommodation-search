import sqlite3
import logging
from db.database import get_connection

logger = logging.getLogger(__name__)

class QuizRepository:
    def __init__(self):
        self.conn = get_connection()
        self.conn.row_factory = sqlite3.Row

    def upsert(self, quiz_id, title, qtype, course_id):
        """Insert or update a quiz."""
        try:
            self.conn.execute("""
                INSERT INTO quiz_store (quiz_id, title, type, course_id)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(quiz_id) DO UPDATE SET
                    title = excluded.title,
                    type = excluded.type,
                    course_id = excluded.course_id
            """, (quiz_id, title, qtype, course_id))
            self.conn.commit()
            logger.info(f"Upserted quiz {quiz_id}: {title}")
        except Exception as e:
            logger.error(f"Error upserting quiz {quiz_id}: {e}")

    def link_to_course(self, course_id, quiz_id):
        """Link quiz to a course in the junction table."""
        try:
            self.conn.execute("""
                INSERT OR IGNORE INTO course_quizzes (course_id, quiz_id)
                VALUES (?, ?)
            """, (course_id, quiz_id))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error linking quiz {quiz_id} to course {course_id}: {e}")

    def get_quiz(self, quiz_id):
        cur = self.conn.execute("SELECT * FROM quiz_store WHERE quiz_id = ?", (str(quiz_id),))
        return cur.fetchone()

    def get_quizzes_by_course(self, course_id):
        cur = self.conn.execute("SELECT * FROM quiz_store WHERE course_id = ?", (str(course_id),))
        return [dict(row) for row in cur.fetchall()]

    def list_all(self):
        cur = self.conn.execute("SELECT quiz_id, title, time_limit, acc_type, course_id FROM quiz_store ORDER BY title")
        return [dict(row) for row in cur.fetchall()]
