import sqlite3
import logging
from db.database import get_connection



logger = logging.getLogger(__name__)

class TermRepository:
    def __init__(self):
        self.conn = get_connection()
        self.conn.row_factory = sqlite3.Row

    def upsert(self, term_id: str, name: str):
        try:
            self.conn.execute("""
                INSERT INTO term_store (term_id, name)
                VALUES (?, ?)
                ON CONFLICT(term_id) DO UPDATE SET name = excluded.name
            """, (term_id, name))
            self.conn.commit()
            logger.info(f"Upserted term: {term_id} - {name}")
        except Exception as e:
            logger.error(f"Error upserting term {term_id}: {e}")

    def link_course(self, term_id: str, course_id: str):
        """Link a course to a term."""
        try:
            self.conn.execute("""
                INSERT OR IGNORE INTO term_courses (term_id, course_id)
                VALUES (?, ?)
            """, (term_id, course_id))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error linking course {course_id} to term {term_id}: {e}")

    def get_term(self, term_id: str):
        cur = self.conn.execute("SELECT * FROM term_store WHERE term_id = ?", (str(term_id),))
        return cur.fetchone()

    def get_courses_for_term(self, term_id: str):
        cur = self.conn.execute("SELECT course_id FROM term_courses WHERE term_id = ?", (str(term_id),))
        return [row['course_id'] for row in cur.fetchall()]

    def list_terms(self):
        cur = self.conn.execute("SELECT term_id, name FROM term_store ORDER BY name")
        return [dict(row) for row in cur.fetchall()]
