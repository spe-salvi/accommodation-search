import sqlite3
import logging
from db.database import get_connection

logger = logging.getLogger(__name__)

class QuestionRepository:
    def __init__(self):
        self.conn = get_connection()
        self.conn.row_factory = sqlite3.Row

    def upsert(self, course_id, quiz_id, item_id, question_type, spell_check):
        """Insert or update question metadata for a quiz item."""
        try:
            self.conn.execute("""
                INSERT INTO question_store (course_id, quiz_id, item_id, question_type, spell_check)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(course_id, quiz_id, item_id) DO UPDATE SET
                    question_type = excluded.question_type,
                    spell_check = excluded.spell_check
            """, (course_id, quiz_id, item_id, question_type, bool(spell_check)))
            self.conn.commit()
            logger.debug(f"Upserted question {item_id} in quiz {quiz_id}, course {course_id}")
        except Exception as e:
            logger.error(f"Error inserting/updating question {item_id}: {e}")

    def get_questions_for_quiz(self, course_id, quiz_id):
        cur = self.conn.execute(
            "SELECT * FROM question_store WHERE course_id = ? AND quiz_id = ?",
            (str(course_id), str(quiz_id))
        )
        return [dict(row) for row in cur.fetchall()]

    def get_essay_questions(self, course_id, quiz_id):
        cur = self.conn.execute(
            "SELECT * FROM question_store WHERE course_id = ? AND quiz_id = ? AND question_type = 'essay'",
            (str(course_id), str(quiz_id))
        )
        return [dict(row) for row in cur.fetchall()]

    def has_spell_check(self, course_id, quiz_id, item_id):
        cur = self.conn.execute("""
            SELECT spell_check FROM question_store
            WHERE course_id = ? AND quiz_id = ? AND item_id = ?
        """, (course_id, quiz_id, item_id))
        row = cur.fetchone()
        return bool(row["spell_check"]) if row else False

    def list_all(self):
        cur = self.conn.execute("SELECT * FROM question_store")
        return [dict(row) for row in cur.fetchall()]