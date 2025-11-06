import sqlite3
import logging
from db.database import get_connection

logger = logging.getLogger(__name__)

class CourseRepository:
    def __init__(self):
        self.conn = get_connection()
        self.conn.row_factory = sqlite3.Row

    def upsert(self, course_id, code, name, term_id):
        """Insert or update a course record."""
        try:
            self.conn.execute("""
                INSERT INTO course_store (course_id, code, name, term_id)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(course_id) DO UPDATE SET
                    code = excluded.code,
                    name = excluded.name,
                    term_id = excluded.term_id
            """, (course_id, code, name, term_id))
            self.conn.commit()
            logger.info(f"Upserted course {course_id} ({name}) in term {term_id}")
        except Exception as e:
            logger.error(f"Error inserting/updating course {course_id}: {e}")

    def link_user(self, course_id, user_id):
        """Create a link between a course and a user."""
        self.conn.execute("""
            INSERT OR IGNORE INTO course_users (course_id, user_id)
            VALUES (?, ?)
        """, (course_id, user_id))
        self.conn.commit()

    def link_quiz(self, course_id, quiz_id):
        """Create a link between a course and a quiz."""
        self.conn.execute("""
            INSERT OR IGNORE INTO course_quizzes (course_id, quiz_id)
            VALUES (?, ?)
        """, (course_id, quiz_id))
        self.conn.commit()

    def get_courses_by_term(self, term_id):
        cur = self.conn.execute("SELECT * FROM course_store WHERE term_id = ?", (str(term_id),))
        return [dict(row) for row in cur.fetchall()]

    def get_users_for_course(self, course_id):
        cur = self.conn.execute("SELECT user_id FROM course_users WHERE course_id = ?", (str(course_id),))
        return [row["user_id"] for row in cur.fetchall()]

    def get_quizzes_for_course(self, course_id):
        cur = self.conn.execute("SELECT quiz_id FROM course_quizzes WHERE course_id = ?", (str(course_id),))
        return [row["quiz_id"] for row in cur.fetchall()]

    def list_courses(self):
        cur = self.conn.execute("SELECT course_id, code, name, term_id FROM course_store ORDER BY name")
        return [dict(row) for row in cur.fetchall()]
