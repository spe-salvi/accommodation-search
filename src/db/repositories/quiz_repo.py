import sqlite3
import logging
from db.database import get_connection

logger = logging.getLogger(__name__)

class QuizRepository:
    def __init__(self):
        self.conn = get_connection()
        self.conn.row_factory = sqlite3.Row

    def upsert(self, quiz_id, title, time_limit, acc_type, quiz_type, course_id):
        """Insert or update a quiz record."""
        print(f"[DEBUG] UPSERT quiz_id={quiz_id}, title={title}, time_limit={time_limit}, acc_type={acc_type}, quiz_type={quiz_type}, course_id={course_id}")
        try:
            self.conn.execute("""
                INSERT INTO quiz_store (quiz_id, title, time_limit, acc_type, quiz_type, course_id)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(quiz_id) DO UPDATE SET
                    title = excluded.title,
                    time_limit = excluded.time_limit,
                    acc_type = excluded.acc_type,
                    quiz_type = excluded.quiz_type,
                    course_id = excluded.course_id
            """, (quiz_id, title, time_limit, acc_type, quiz_type, course_id))

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
        """Return all quizzes linked to a specific course."""
        cur = self.conn.execute("""
            SELECT q.quiz_id, q.title, q.time_limit, q.acc_type, q.quiz_type, q.course_id
            FROM quiz_store q
            JOIN course_quizzes cq ON q.quiz_id = cq.quiz_id
            WHERE cq.course_id = ?
        """, (course_id,))
        return [dict(row) for row in cur.fetchall()]

    def list_all(self):
        cur = self.conn.execute("SELECT quiz_id, title, time_limit, acc_type, quiz_type, course_id FROM quiz_store ORDER BY title")
        return [dict(row) for row in cur.fetchall()]
